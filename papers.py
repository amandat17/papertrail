from pathlib import Path

import pymupdf

def extract_pages(path: Path) -> list[dict]:
    # Extract PDF text and keep its page numbers

    # Make sure the file exists before opening it
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages = []

    #Open the PDF and automatically close it when finished
    with pymupdf.open(path) as document:

        #This version doesn't handle password-protected PDFs
        if document.needs_pass:
            raise ValueError("Password-protected PDFs are unsupported")

        # enumerate() gives us each page and its index, starting at 0
        for index, page in enumerate(document):

            #Extract text in an approximate reading order
            #strip() removes whitespace from the beginning and end
            text = page.get_text("text", sort=True).strip()

            #Store the page number and its extracted text
            #Add 1 because PDF page numbering should start at 1
            pages.append({
                "page": index + 1,
                "text": text,
            })
    
    # Reject PDFs with no extractable text
    # Scanned documents may need OCR, which we haven't implemented
    if not any(page["text"] for page in pages):
        raise ValueError(
            "No readable text found"
            "Scanned PDFs may require Optical Character Recognition"
        )
    return pages
