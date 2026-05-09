import re

import streamlit as st

from chat import render_chat_tab
from docs import (
    LessonDocument,
    get_lesson_documents,
    read_index_document,
    read_lesson_document,
)


def main() -> None:
    st.set_page_config(page_title="ChatLab", layout="wide")

    st.title("ChatLab")

    selected_tab = render_navigation()

    if selected_tab == "홈":
        render_home_tab()
    elif selected_tab == "설명":
        render_docs_tab()
    else:
        render_chat_tab()


def render_navigation() -> str:
    tabs = ["홈", "설명", "챗봇"]
    requested_tab = st.query_params.get("tab", "홈")
    initial_tab = requested_tab if requested_tab in tabs else "홈"

    selected_tab = st.segmented_control(
        "화면",
        options=tabs,
        default=initial_tab,
        label_visibility="collapsed",
    )

    if selected_tab != st.query_params.get("tab"):
        st.query_params["tab"] = selected_tab

    return selected_tab


def render_home_tab() -> None:
    st.markdown(_render_internal_links(read_index_document()), unsafe_allow_html=True)


def render_docs_tab() -> None:
    documents = get_lesson_documents()

    if not documents:
        st.info("표시할 학습 문서가 없습니다.")
        return

    list_column, viewer_column = st.columns([1, 3], gap="large")

    with list_column:
        selected_document = render_document_list(documents)

    with viewer_column:
        content = read_lesson_document(selected_document)
        st.markdown(content)


def render_document_list(documents: list[LessonDocument]) -> LessonDocument:
    requested_doc = st.query_params.get("doc")
    document_ids = [document.document_id for document in documents]
    initial_index = document_ids.index(requested_doc) if requested_doc in document_ids else 0

    selected_title = st.radio(
        "문서 목록",
        options=[document.title for document in documents],
        index=initial_index,
        label_visibility="visible",
    )

    selected_document = next(document for document in documents if document.title == selected_title)

    if st.query_params.get("doc") != selected_document.document_id:
        st.query_params["doc"] = selected_document.document_id

    return selected_document


def _render_internal_links(markdown_text: str) -> str:
    return re.sub(
        r"\[([^\]]+)\]\((\?tab=[^)]+)\)",
        r'<a href="\2" target="_self">\1</a>',
        markdown_text,
    )


if __name__ == "__main__":
    main()
