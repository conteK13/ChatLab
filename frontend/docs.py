import base64
import html
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = PROJECT_ROOT / "docs" / "lessons"
INDEX_DOCUMENT_NAME = "index.md"
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


@dataclass(frozen=True)
class LessonDocument:
    document_id: str
    title: str
    path: Path


def get_lesson_documents(lessons_dir: Path = LESSONS_DIR) -> list[LessonDocument]:
    if not lessons_dir.exists():
        return []

    documents = [
        LessonDocument(document_id=path.stem, title=_format_title(path), path=path)
        for path in lessons_dir.glob("*.md")
        if path.is_file() and path.name != INDEX_DOCUMENT_NAME
    ]

    return sorted(documents, key=lambda document: _sort_key(document.path))


def read_index_document(lessons_dir: Path = LESSONS_DIR) -> str:
    index_path = lessons_dir / INDEX_DOCUMENT_NAME
    if not index_path.exists():
        return "# ChatLab\n\n학습 문서 홈을 준비하고 있습니다."

    return index_path.read_text(encoding="utf-8")


def read_lesson_document(document: LessonDocument) -> str:
    content = document.path.read_text(encoding="utf-8")
    return _embed_relative_images(content, document.path.parent)


def _embed_relative_images(markdown_text: str, base_dir: Path) -> str:
    def replace_image(match: re.Match[str]) -> str:
        alt_text = match.group(1)
        image_reference = match.group(2)

        if re.match(r"^(https?://|data:)", image_reference):
            return match.group(0)

        image_path = Path(image_reference)
        if not image_path.is_absolute():
            image_path = base_dir / image_path

        if not image_path.exists() or not image_path.is_file():
            return match.group(0)

        mime_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
        escaped_alt_text = html.escape(alt_text, quote=True)

        return (
            f'<img src="data:{mime_type};base64,{encoded_image}" '
            f'alt="{escaped_alt_text}" style="max-width: 100%; height: auto;" />'
        )

    return MARKDOWN_IMAGE_PATTERN.sub(replace_image, markdown_text)


def _format_title(path: Path) -> str:
    stem = path.stem

    parts = stem.split("_", maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1].replace("_", " ")

    return stem.replace("_", " ")


def _sort_key(path: Path) -> tuple[int, int, str]:
    stem = path.stem

    if stem == "index":
        return (-1, -1, stem)

    prefix = stem.split("_", maxsplit=1)[0]
    if prefix.isdigit():
        return (0, int(prefix), stem)

    return (1, 0, stem)
