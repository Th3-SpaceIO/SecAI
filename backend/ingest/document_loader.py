
#===============================#
#       DOCUMENT LOADER
#===============================#



from pathlib import Path
import os
import pandas as pd
import docx #to handle word
from docx import Document
from reportlab.pdfgen import canvas
import pdfplumber #to handle pdfs
from PIL import Image
from charset_normalizer import from_path  #this is used to detect the encoding of text files




class DocumentLoader:
    def __init__(self):
        #CURRENTLY SUPPORTED FILE TYPES AND CORRESPONGING HANDLERS
        self.supported_types = {
            ".pdf" : self._load_pdf,
            ".docx" : self._load_docx,
            ".txt" : self._load_txt,
            ".csv" : self._load_csv,
            ".jpeg" : self._load_image,
            ".jpg" : self._load_image,
            ".png" : self._load_image,
        }

    #LOADS THE DOCUMENT BASED ON THE FILE PATH PROVIDED
    def load_document(self, file_path):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        

        file_type = path.suffix.lower()
        if file_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_type}")
    
        """IDENTIFY THE FILE TYPE AND CALL THE APPROPRIATE HANDLER TO EXTRACT TEXT AND METADATA"""
        text, metadata = self.supported_types[file_type](path)

        return {
            "text": text,
            "metadata": {
                "file_name": path.name,
                "file_type": file_type,
                "source_path": str(path.resolve()),
                **metadata
            }
        }
        

        # ---------- Handlers ----------

    def _load_pdf(self, path: Path):
        try:
            text = ""
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return text, {"pages": len(pdf.pages)}
        except Exception as e:
            raise ValueError(f"Error loading PDF file: {e}")




    def _load_docx(self, path: Path):
        try:
            doc = docx.Document(path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text, {"paragraphs": len(doc.paragraphs)}
        except Exception as e:
            raise ValueError(f"Error loading DOCX file: {e}")



    def _load_txt(self, path: Path):
        try:
            result = from_path(path).best()
            text = str(result)
            return text, {"encoding": result.encoding}
        except Exception as e:
            raise ValueError(f"Error loading text file: {e}")
        


    def _load_csv(self, path: Path):
        try:
            df = pd.read_csv(path)
            return df.to_string(index=False), {"rows": len(df)}
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")


    def _load_image(self, path: Path):
        """COMING SOON"""
        pass





if __name__ == "__main__":
    try:
        Path("test_files").mkdir(exist_ok=True)

        # REAL PDF
        c = canvas.Canvas("test_files/sample.pdf")
        c.drawString(100, 750, "hello welcome to python this is a sample pdf file")
        c.save()

        # DOCX
        doc = Document()
        doc.add_paragraph("hello welcome to python this is a sample docx file")
        doc.save("test_files/sample.docx")

        # TXT
        with open("test_files/sample.txt", "w", encoding="utf-8") as f:
            f.write("hello welcome to python this is a sample txt file")

        # CSV
        with open("test_files/sample.csv", "w", encoding="utf-8") as f:
            f.write("name,age\nAlice,30\nBob,25")

        loader = DocumentLoader()

        for file in [
            "test_files/sample.pdf",
            "test_files/sample.docx",
            "test_files/sample.txt",
            "test_files/sample.csv"
        ]:
            result = loader.load_document(file)
            print(f"Loaded {file}:")
            print(result)
            print("\n" + "=" * 50 + "\n")

    except Exception as e:
        print(f"Error during testing: {e}")