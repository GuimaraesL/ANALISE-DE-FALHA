# pdf_as_image_converter.py responsavel por converter pdf em imagens
from pathlib import Path
from typing import List
from pdf2image import convert_from_path
import tempfile
import os

class PDFAsImageConverter:
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "pdf_as_images"
        self.temp_dir.mkdir(exist_ok=True)

    def convert(self, pdf_path: Path) -> List[Path]:
        images = convert_from_path(str(pdf_path), dpi=200, poppler_path=r"C:\Users\GuimaraesL\poppler\poppler-24.08.0\Library\bin")
        image_paths = []
        base_name = pdf_path.stem
        for i, img in enumerate(images):
            img_path = self.temp_dir / f"{base_name}_page_{i+1}.jpg"
            img.save(img_path, "JPEG")
            image_paths.append(img_path)
        return image_paths

    def cleanup(self):
        for file in self.temp_dir.glob("*.jpg"):
            try:
                os.remove(file)
            except:
                pass