from pathlib import Path
import re

import arxiv
import pymupdf
import requests


def search_papers(query: str) -> list[arxiv.Result]:
    """Find up to five papers matching an arXiv query."""
    if not query.strip():
        raise ValueError("Enter a nonempty search topic.")

    # Space API requests apart and retry temporary failures.
    client = arxiv.Client(
        page_size=5,
        delay_seconds=3,
        num_retries=2,
    )

    search = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    return list(client.results(search))


def download_paper(
    paper: arxiv.Result,
    folder: Path = Path("papers"),
) -> Path:
    """Download a paper and check that it is a readable PDF."""
    if not paper.pdf_url:
        raise ValueError("This paper has no PDF download link.")

    folder.mkdir(parents=True, exist_ok=True)

    # Use the arXiv ID, rather than the title, as a safe filename.
    paper_id = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        paper.get_short_id(),
    )

    pdf_path = folder / f"{paper_id}.pdf"
    temporary_path = folder / f"{paper_id}.part"

    try:
        # Download in chunks rather than loading everything into memory.
        with requests.get(
            paper.pdf_url,
            stream=True,
            timeout=(10, 60),
        ) as response:
            response.raise_for_status()

            total_bytes = 0

            with temporary_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=65536):
                    if not chunk:
                        continue

                    total_bytes += len(chunk)

                    if total_bytes > 25 * 1024 * 1024:
                        raise ValueError(
                            "PDF exceeds the 25 MB download limit."
                        )

                    file.write(chunk)

        # A successful HTTP response might still contain an error page.
        # Confirm the downloaded file actually opens as a PDF.
        with pymupdf.open(temporary_path) as document:
            if not document.is_pdf or document.page_count == 0:
                raise ValueError("The download is not a valid PDF.")

        # Only replace the destination after the download is valid.
        temporary_path.replace(pdf_path)

    finally:
        # Remove an incomplete download if anything failed.
        temporary_path.unlink(missing_ok=True)

    return pdf_path