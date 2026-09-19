import pymupdf


class PDFParser:

    def parse(self, pdf_bytes: bytes) -> list[dict]:
        pages = []

        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:

            for page_number, page in enumerate(document, start=1):

                text = page.get_text().strip()

                if not text:
                    continue

                pages.append({
                    "page": page_number,
                    "text": text,
                })

        return pages