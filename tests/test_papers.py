import pymupdf
import pytest

from papers import extract_pages

def test_extract_pages_preserves_text_and_page_numbers(tmp_path):
    #Create a temporary two-page PDF with known text
    pdf_path = tmp_path / "example.pdf"

    with pymupdf.open() as document:
        first_page = document.new_page()
        first_page.insert_text((72,72), "First page content")

        second_page = document.new_page()
        second_page.insert_text((72, 72), "Second page content")

        document.save(pdf_path)
    
    #Check that extraction returns the correct text and page numbers
    pages = extract_pages(pdf_path)

    assert len(pages)==2
    assert pages[0]["page"] ==1
    assert "First page content" in pages[0]["text"]
    assert pages[1]["page"] ==2
    assert "Second page content" in pages[1]["text"]

def test_missing_pdf_raises_error(tmp_path):
    # A nonexistent file should produce a clear error
    with pytest.raises(FileNotFoundError):
        extract_pages(tmp_path / "missing.pdf")

def test_blank_pdf_raises_error(tmp_path):
    #Create a valid PDF that contains no readable text
    pdf_path = tmp_path / "blank.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.save(pdf_path)

    with pytest.raises(ValueError, match = "No readable text"):
        extract_pages(pdf_path)