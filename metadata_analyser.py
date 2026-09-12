import re
from abc import ABC, abstractmethod
from PIL import Image
import mimetypes
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import docx


# esta clase no se puede llamar, solo puede hacer que hereden de ella (ABC)
class MetadataExtractor(ABC):
    @abstractmethod
    # metodo obligatorio para las clases que hereden de esta
    def extract(self, filepath):
        pass

class ImageMetadataExtractor(MetadataExtractor):
    def extract(self, filepath):
        with Image.open(filepath) as img:
            if img.format in ["JPG", "JPEG"]:
                # Exchangeable Image File Format, son los metadatos estandar de las camaras(gps,etc)
                exif = img._getexif()
                if exif:
                    return {Image.ExifTags.TAGS.get(key, key): value # traduce el número clave (ej. 306) a su nombre en texto legible
                            # recorre el dict y filtra solo aquellas claves que Pillow conoce en su dict de nombres legibles
                            for key, value in exif.items() if key in Image.ExifTags.TAGS} 
                else:
                    return {"Error": "No EXIF metadata found"}

            elif img.format in ["PNG"]:
                if img.info:
                    # si hay metadatos de la img png devuelve el dict con los meta
                    return img.info
                else:
                    return {"Error": "No metadata found"}
            else:
                return {"Error": "Unsupported img format"}

class PdfMetadataExtractor(MetadataExtractor):
    def extract(self, filepath):
        metadata = {}
        # lo leemos en binario
        with open(filepath, "rb") as f:
            parser = PDFParser(f)
            doc = PDFDocument(parser)
            if doc.info:
                # si hay metadatos los recorremos
                for info in doc.info:
                    # recorremos cada metadato que es un dict
                    for k, v in info.items():
                        # comprobamos si el value de cada metadato esta en bytes
                        if isinstance(v, bytes):
                            try:
                                # si esta en byte lo decodificamos en utf 16
                                decoded_value = v.decode("utf-16be")
                            except UnicodeDecodeError:
                                # si no se puede lo dejos en utf 8 y ignoramos errores
                                decoded_value = v.decode("utf-8", errors="ignore")
                        else:
                            # si no esta en bytes dejamos igual el value
                            decoded_value = v
                            # añadimos a nuestro dict el value decodificado
                        metadata[k] = decoded_value

            # extraemos el contenido del fichero
            text = extract_text(filepath)
            # añadimos a nuestro dict metatdata emails que encontremos en el fichero
            metadata["Emails"] = self._extract_email(text)

        return metadata

    def _extract_email(self, text):
        """ metodo interno para buscar emails en ficheros de texto con regex """
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        # le pasamos la regex de email y el contenido del fichero para que encuentre emails
        return re.findall(email_regex, text)

class DocxMetadataExtractor(MetadataExtractor):
    def extract(self, filepath):
        doc = docx.Document(filepath)
        # sacamos las propiedades principales
        prop = doc.core_properties
        attributes = [
            "author", "category", "comments", "content_status",
            "created", "identifier", "keywords", "last_modified_by",
            "language", "modified", "subject", "title", "version"
        ]
        # guaradmos en este dict los meta
        metadata = {attr: getattr(prop, attr, None) for attr in attributes} # recorremos el array de atributos que buscamos
        return metadata


class MetadataExtractorFactory:
    @staticmethod
    # metodo estatica que no necesita self
    def get_extractor(filepath):
        # guardamos el mime type del fichero con el metodo de la libreria mymetypes, el metodo devuelve dos valores por lo q usamos _ para ignorarlo
        mime_type, _ = mimetypes.guess_type(filepath) # identifica la naturaleza real del archivo mediante su contenido o extensión
        if mime_type:
            if mime_type.startswith("image"):
                return ImageMetadataExtractor()
            if mime_type == "application/pdf":
                return PdfMetadataExtractor()
            if mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return DocxMetadataExtractor()
        raise ValueError("Unsupported file type")    
            

def extract_metadata(filepath):
    """ metodo puente para llamar desde fuera """
    extractor = MetadataExtractorFactory.get_extractor(filepath)
    return extractor.extract(filepath)