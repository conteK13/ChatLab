from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = PROJECT_ROOT / "docs" / "lessons"
INDEX_DOCUMENT_NAME = "index.md"


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
    return document.path.read_text(encoding="utf-8")


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
