#===============================#
#       DOCUMENT LOADER
#===============================#

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import docx
import pandas as pd
import pdfplumber
from charset_normalizer import from_path

from chunker import DocumentChunker

logger = logging.getLogger(__name__)

# Type alias for what each sub-loader returns
LoaderResult = Tuple[str, Dict[str, Any]]

# Safety cap for CSV serialization
_CSV_ROW_LIMIT = 10_000


class DocumentLoader:
    def __init__(self) -> None:
        self.supported_types: Dict[str, Callable[[Path], LoaderResult]] = {
            ".pdf":  self._load_pdf,
            ".docx": self._load_docx,
            ".txt":  self._load_txt,
            ".csv":  self._load_csv,
            ".jpeg": self._load_image,
            ".jpg":  self._load_image,
            ".png":  self._load_image,
        }

    # ===============================
    #       MAIN ENTRY POINT
    # ===============================
    def load_document(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Load a document from disk and return its content and metadata.

        Args:
            file_path: Path to the file to load.

        Returns:
            dict with 'content' (str) and 'metadata' (dict).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file type is unsupported or content is unreadable.
            NotImplementedError: If the file type has a pending implementation.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Distinguish missing file from a path that exists but isn't a file
        # (e.g. a directory was passed)
        if not path.is_file():
            raise ValueError(f"Path exists but is not a file: {file_path}")

        file_type = path.suffix.lower()

        if file_type not in self.supported_types:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. "
                f"Supported: {sorted(self.supported_types)}"
            )

        content, extra_metadata = self.supported_types[file_type](path)

        return {
            "content": content,
            "metadata": {
                "file_name":   path.name,
                "file_type":   file_type,
                "source_path": str(path.resolve()),
                "file_size":   path.stat().st_size,
                # BUG FIX: use SHA-256 instead of MD5
                "file_hash":   self._hash_file(path),
                **extra_metadata,
            },
        }

    # ===============================
    #           PDF LOADER
    # ===============================
    def _load_pdf(self, path: Path) -> LoaderResult:
        # BUG FIX: guard is outside the try block so our own ValueError
        # isn't re-wrapped into a generic message.
        try:
            pages_text = []
            with pdfplumber.open(path) as pdf:
                num_pages = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pages_text.append(page_text.strip())
        except Exception as e:
            # BUG FIX: `raise ... from e` preserves the original traceback
            raise ValueError(f"Failed to open or parse PDF: {path.name}") from e

        if not pages_text:
            raise ValueError(f"No extractable text found in PDF: {path.name}")

        return "\n".join(pages_text), {"pages": num_pages}

    # ===============================
    #           DOCX LOADER
    # ===============================
    def _load_docx(self, path: Path) -> LoaderResult:
        try:
            doc = docx.Document(path)
            paragraphs = [
                p.text.strip()
                for p in doc.paragraphs
                if p.text and p.text.strip()
            ]
        except Exception as e:
            raise ValueError(f"Failed to open or parse DOCX: {path.name}") from e

        if not paragraphs:
            raise ValueError(f"No extractable text found in DOCX: {path.name}")

        return "\n".join(paragraphs), {"paragraphs": len(paragraphs)}

    # ===============================
    #           TXT LOADER
    # ===============================
    def _load_txt(self, path: Path) -> LoaderResult:
        try:
            result = from_path(path).best()
        except Exception as e:
            raise ValueError(f"Failed to read text file: {path.name}") from e

        if result is None:
            raise ValueError(f"Could not detect encoding for: {path.name}")

        text = str(result)
        if not text.strip():
            raise ValueError(f"Text file is empty or unreadable: {path.name}")

        # BUG FIX: only include confidence if it's actually available
        extra: Dict[str, Any] = {"encoding": result.encoding}
        confidence = getattr(result, "confidence", None)
        if confidence is not None:
            extra["confidence"] = confidence

        return text.strip(), extra

    # ===============================
    #           CSV LOADER
    # ===============================
    def _load_csv(self, path: Path) -> LoaderResult:
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {path.name}") from e

        if df.empty:
            raise ValueError(f"CSV file is empty: {path.name}")

        total_rows = len(df)

        # BUG FIX: cap serialization to avoid memory blowouts on large files
        if total_rows > _CSV_ROW_LIMIT:
            logger.warning(
                "CSV has %d rows; only the first %d will be serialized to text.",
                total_rows, _CSV_ROW_LIMIT,
            )
            df = df.head(_CSV_ROW_LIMIT)

        text = df.to_string(index=False)

        return text.strip(), {
            "rows":         total_rows,
            "columns":      len(df.columns),
            "column_names": list(df.columns),       # added: useful for downstream search
            "truncated":    total_rows > _CSV_ROW_LIMIT,
        }

    # ===============================
    # IMAGE LOADER (PLACEHOLDER)
    # ===============================
    def _load_image(self, path: Path) -> LoaderResult:
        raise NotImplementedError(
            f"Image loading is not yet implemented (file: {path.name}). "
            "Consider integrating a vision model or OCR library."
        )

    # ===============================
    #   FILE HASH (DEDUPLICATION)
    # ===============================
    @staticmethod
    def _hash_file(path: Path) -> str:
        # BUG FIX: SHA-256 instead of MD5; collision-resistant for deduplication
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()


#================================#
#       TEST ENTRY POINT         #
#================================#

def main() -> None:
    loader = DocumentLoader()
    file_path = Path("test_files/sample.docx")

    try:
        result = loader.load_document(file_path)

        print("\n==============================")
        print(" DOCUMENT LOADED SUCCESSFULLY")
        print("==============================\n")
        print("CONTENT PREVIEW:")
        print(result["content"][:500])
        print("\nMETADATA:")
        for key, value in result["metadata"].items():
            print(f"  {key}: {value}")

    except (FileNotFoundError, ValueError, NotImplementedError) as e:
        # Catch specific expected errors, let unexpected ones propagate
        print("\n==============================")
        print(" ERROR LOADING DOCUMENT")
        print("==============================\n")
        print(str(e))


if __name__ == "__main__":
    main()