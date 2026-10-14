import argparse
import json
from pathlib import Path

from arxiv_search import search_papers, download_paper
from papers import extract_pages
from summarizer import summarize_paper
from export import save_markdown


def choose_paper(results):
    """Display search results and ask the user to choose one."""
    for number, paper in enumerate(results, start=1):
        authors = ", ".join(
            author.name for author in paper.authors[:3]
        )

        if len(paper.authors) > 3:
            authors += ", et al."

        print(f"\n{number}. {paper.title}")
        print(f"   Authors: {authors}")
        print(f"   Published: {paper.published.date()}")
        print(f"   Link: {paper.entry_id}")

    while True:
        selection = input(
            f"\nChoose a paper (1–{len(results)}) or q to quit: "
        ).strip()

        if selection.lower() == "q":
            return None

        try:
            number = int(selection)
        except ValueError:
            print("Enter a number or q.")
            continue

        if 1 <= number <= len(results):
            return results[number - 1]

        print(f"Choose a number between 1 and {len(results)}.")


def main():
    parser = argparse.ArgumentParser(
        description="Find and summarize research PDFs."
    )

    # Require exactly one input: a local PDF or a search query.
    source = parser.add_mutually_exclusive_group(required=True)

    source.add_argument(
        "--pdf",
        type=Path,
        help="Path to a local PDF.",
    )

    source.add_argument(
        "--query",
        help="Topic or arXiv query to search for.",
    )

    # Let us test search, download, and extraction without calling Codex.
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Save extracted text without generating a summary.",
    )

    args = parser.parse_args()
    metadata = None

    if args.query is not None:
        print(f"Searching arXiv for: {args.query}")
        results = search_papers(args.query)

        if not results:
            print("No matching papers found. Try a different query.")
            return

        paper = choose_paper(results)

        if paper is None:
            print("Cancelled.")
            return

        print(f"\nDownloading: {paper.title}")
        pdf_path = download_paper(paper)

        # Keep source information alongside the generated results.
        metadata = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "arxiv_url": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "published": paper.published.isoformat(),
        }

    else:
        pdf_path = args.pdf

    pages = extract_pages(pdf_path)
    print(f"Extracted {len(pages)} pages.")

    output_folder = Path("outputs") / pdf_path.stem
    output_folder.mkdir(parents=True, exist_ok=True)

    (output_folder / "pages.json").write_text(
        json.dumps(pages, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    if metadata is not None:
        (output_folder / "source.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    if args.extract_only:
        print(f"Saved extracted text to {output_folder / 'pages.json'}")
        print("No new summary was generated.")
        return

    # Detect long inputs before requesting a summary.
    character_count = len(json.dumps(pages, ensure_ascii=False))

    if character_count > 60000:
        raise ValueError(
            f"This paper contains {character_count:,} serialized "
            "characters, exceeding the 60,000-character limit. "
            "Extracted text was saved; choose a shorter paper."
        )

    print("Asking Codex to summarize the paper...")
    summary = summarize_paper(pages)

    summary_path = output_folder / "summary.json"
    summary_path.write_text(
        summary.model_dump_json(indent=2),
        encoding="utf-8",
    )

    markdown_path = output_folder / "summary.md"
    save_markdown(summary, markdown_path)

    print(f"Saved JSON summary to {summary_path}")
    print(f"Saved Markdown summary to {markdown_path}")
    print("\nOverview:")
    print(summary.overview)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        raise SystemExit(130)
    except Exception as error:
        print(f"Error: {error}")
        raise SystemExit(1)