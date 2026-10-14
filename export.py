from pathlib import Path

from schemas import PaperSummary


def save_markdown(summary: PaperSummary, path: Path) -> None:
    """Turn a structured summary into a readable Markdown file."""

    # Each entry becomes a line in the output file.
    lines = [
        "# Research Paper Summary",
        "",
        "## Overview",
        summary.overview,
        "",
        "## Methods",
    ]

    # Add each method as a bullet.
    for method in summary.methods:
        lines.append(f"- {method}")

    lines.extend(["", "## Findings"])

    # Include page references beside each finding.
    for finding in summary.findings:
        pages = ", ".join(str(page) for page in finding.pages)
        lines.append(f"- {finding.claim} (PDF pages: {pages})")

    lines.extend(["", "## Limitations"])

    for limitation in summary.limitations:
        lines.append(f"- {limitation}")

    lines.extend([
        "",
        "---",
        "AI-generated summary. Check claims against the original PDF.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)

    # Join the lines with newline characters and save the file.
    path.write_text("\n".join(lines), encoding="utf-8")