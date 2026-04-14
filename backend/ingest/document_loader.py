#===============================#
#       DOCUMENT LOADER
#===============================#

from pathlib import Path
import pandas as pd
import docx
import pdfplumber
import hashlib
from charset_normalizer import from_path
from chunker import DocumentChunker


class DocumentLoader:
    def __init__(self):
        self.supported_types = {
            ".pdf": self._load_pdf,
            ".docx": self._load_docx,
            ".txt": self._load_txt,
            ".csv": self._load_csv,
            ".jpeg": self._load_image,
            ".jpg": self._load_image,
            ".png": self._load_image,
        }

    # ===============================
    #       MAIN ENTRY POINT
    # ===============================
    def load_document(self, file_path):
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = path.suffix.lower()

        if file_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_type}")

        content, metadata = self.supported_types[file_type](path)

        return {
            "content": content,
            "metadata": {
                "file_name": path.name,
                "file_type": file_type,
                "source_path": str(path.resolve()),
                "file_size": path.stat().st_size,
                "file_hash": self._hash_file(path),
                **metadata
            }
        }

    # ===============================
    #           PDF LOADER
    # ===============================
    def _load_pdf(self, path: Path):
        try:
            pages_text = []

            with pdfplumber.open(path) as pdf:
                num_pages = len(pdf.pages)

                for page in pdf.pages:
                    page_text = page.extract_text()

                    if page_text and page_text.strip():
                        pages_text.append(page_text.strip())

            if not pages_text:
                raise ValueError("No extractable text found in PDF")

            return "\n".join(pages_text), {
                "pages": num_pages
            }

        except Exception as e:
            raise ValueError(f"Error loading PDF file: {e}")

    # ===============================
    #           DOCX LOADER
    # ===============================
    def _load_docx(self, path: Path):
        try:
            doc = docx.Document(path)

            paragraphs = [
                p.text.strip()
                for p in doc.paragraphs
                if p.text and p.text.strip()
            ]

            if not paragraphs:
                raise ValueError("No extractable text found in DOCX")

            return "\n".join(paragraphs), {
                "paragraphs": len(paragraphs)
            }

        except Exception as e:
            raise ValueError(f"Error loading DOCX file: {e}")

    # ===============================
    #        TXT LOADER (FIXED)
    # ===============================
    def _load_txt(self, path: Path):
        try:
            result = from_path(path).best()

            if result is None:
                raise ValueError("Could not detect encoding")

            text = str(result)

            if not text.strip():
                raise ValueError("TXT file is empty or unreadable")

            return text.strip(), {
                "encoding": result.encoding,
                "confidence": getattr(result, "confidence", None)
            }

        except Exception as e:
            raise ValueError(f"Error loading text file: {e}")

    # ===============================
    #           CSV LOADER
    # ===============================
    def _load_csv(self, path: Path):
        try:
            df = pd.read_csv(path)

            if df.empty:
                raise ValueError("CSV file is empty")

            text = df.to_string(index=False)

            return text.strip(), {
                "rows": len(df),
                "columns": len(df.columns)
            }

        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")

    # ===============================
    # IMAGE LOADER (PLACEHOLDER)
    # ===============================
    def _load_image(self, path: Path):
        raise NotImplementedError("Image loading not implemented yet")

    # ===============================
    #   FILE HASH (DEDUPLICATION)
    # ===============================
    def _hash_file(self, path: Path):
        hasher = hashlib.md5()

        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        return hasher.hexdigest()


# ===============================#
#    TEST ENTRY POINT            #
#================================#






def main():
    loader = DocumentLoader()

    file_path = Path("test_files/sample.txt")

    try:
        result = loader.load_document(file_path)

        print("\n==============================")
        print("DOCUMENT LOADED SUCCESSFULLY")
        print("==============================\n")

        print("CONTENT:")
        print(result["content"][:500])  # preview only

        print("\nMETADATA:")
        for key, value in result["metadata"].items():
            print(f"{key}: {value}")

    except Exception as e:
        print("\n==============================")
        print("ERROR LOADING DOCUMENT")
        print("==============================\n")
        print(str(e))


if __name__ == "__main__":
    main()