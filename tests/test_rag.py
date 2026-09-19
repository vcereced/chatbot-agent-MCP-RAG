import requests
from pathlib import Path


BASE_URL = "http://rag:8000"
PDF_PATH = Path(__file__).parent / "fixtures" / "ejemplo.pdf"

def test_ingest_documents():
    with PDF_PATH.open("rb") as pdf:

        response = requests.post(
            f"{BASE_URL}/ingest_documents",
            files={
                "file": (
                    "test.pdf",
                    pdf,
                    "application/pdf",
                )
            },
            timeout=30,
        )


    assert response.status_code == 200

    data = response.json()

    assert "chunks" in data
    assert isinstance(data["chunks"], int)
    assert data["chunks"] > 0

# if __name__ == "__main__":
#     test_ingest_documents()