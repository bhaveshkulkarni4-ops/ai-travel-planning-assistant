from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_web_page(url: str, output_file: Path, title: str) -> None:
    print(f"Fetching: {title}")

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that are not useful for the knowledge base.
    for element in soup(
        ["script", "style", "nav", "footer", "header", "noscript"]
    ):
        element.decompose()

    text = soup.get_text("\n")

    # Clean excessive blank lines.
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    content = "\n".join(lines)

    output = f"""# {title}

Source URL:
{url}

---

{content}
"""

    output_file.write_text(output, encoding="utf-8")

    print(f"Saved: {output_file}")


def fetch_pdf(url: str, output_file: Path, title: str) -> None:
    print(f"Fetching: {title}")

    pdf_path = DOCUMENTS_DIR / "_temporary_source.pdf"

    response = requests.get(
        url,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    response.raise_for_status()

    pdf_path.write_bytes(response.content)

    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    content = "\n\n".join(pages)

    output = f"""# {title}

Source URL:
{url}

---

{content}
"""

    output_file.write_text(output, encoding="utf-8")

    pdf_path.unlink(missing_ok=True)

    print(f"Saved: {output_file}")


def main() -> None:

    # Source 1: Visit Singapore — 4-day itinerary
    fetch_pdf(
    "https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/q4-singapore-insider-2019-en.pdf",
    DOCUMENTS_DIR / "visit_singapore_itineraries.md",
    "Visit Singapore — Singapore Travel Guide",
)

    # Source 2: Visit Singapore Travel Guide
    fetch_pdf(
    "https://www.visitsingapore.com/content/dam/desktop/global/about-singapore/traveller-information/q3_singapore-insider-2019_en.pdf",
    DOCUMENTS_DIR / "visit_singapore_travel_guide.md",
    "Visit Singapore — Travel Guide",
)

    # Source 3: Wikivoyage
    fetch_web_page(
        "https://en.wikivoyage.org/wiki/Singapore",
        DOCUMENTS_DIR / "wikivoyage_singapore.md",
        "Wikivoyage — Singapore Travel Guide",
    )

    print("\nKnowledge-base source acquisition completed.")


if __name__ == "__main__":
    main()