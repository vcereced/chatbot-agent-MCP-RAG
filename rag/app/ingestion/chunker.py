class TextChunker:

    SEPARATORS = [
        "\n\n",  # párrafos
        "\n",    # líneas
        ". ",    # frases
        " ",     # palabras
        "",      # caracteres
    ]
    def __init__(self, max_size: int = 1000, overlap: int = 150):
        self.max_size = max_size
        self.overlap = overlap

    def chunk(self, pages: list[dict]) -> list[dict]:

        chunks = []

        for page in pages:
            page_chunks = self._split_recursive(
                page["text"],
                self.SEPARATORS,
                self.max_size,
            )

            # Aplicar overlap
            page_chunks = self._add_overlap(
                page_chunks,
                self.overlap,
            )

            for text in page_chunks:
                chunks.append({
                    "page": page["page"],
                    "text": text,
                })

        return chunks

    def _split_recursive(
        self,
        text: str,
        separators: list[str],
        max_size: int,
    ) -> list[str]:

        text = text.strip()

        if len(text) <= max_size:
            return [text]

        if not separators:
            return [
                text[i:i + max_size]
                for i in range(0, len(text), max_size)
            ]

        separator = " "
        remaining = separators[1:]

        parts = text.split(separator)

        chunks = []
        current = ""

        for part in parts:

            part = part.strip()

            if not part:
                continue

            candidate = (
                part
                if not current
                else current + separator + part
            )

            if len(candidate) <= max_size:
                current = candidate
                continue

            # El candidate no cabe
            if current:
                current = current.replace("\n", " ")
                chunks.append(current)
                current = ""

            # El fragmento individual cabe
            if len(part) <= max_size:
                current = part

            # El fragmento es demasiado grande:
            # bajamos al siguiente separador
            else:
                chunks.extend(
                    self._split_recursive(
                        part,
                        remaining,
                        max_size,
                    )
                )

        if current:
            chunks.append(current)

        return chunks

    def _add_overlap(
        self,
        chunks: list[str],
        overlap: int,
    ) -> list[str]:

        if overlap <= 0 or len(chunks) <= 1:
            return chunks

        result = [chunks[0]]

        for i in range(1, len(chunks)):

            previous = chunks[i - 1]

            # Cogemos los últimos `overlap` caracteres
            # del chunk anterior
            overlap_text = previous[-overlap:]

            # Evitamos empezar en mitad de una palabra
            space = overlap_text.find(" ")

            if space != -1:
                overlap_text = overlap_text[space + 1:]

            current = overlap_text + " " + chunks[i]

            result.append(current)

        return result