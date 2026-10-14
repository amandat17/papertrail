## PaperTrail

A Python research-paper assistant that summarizes PDFs with page
references and exports results as JSON and Markdown.

## Features

- Searches arXiv and downloads a user-selected paper.
- Saves paper titles, authors, and source links.
- Extracts PDF text while preserving page numbers.
- Generates structured overviews, methods, findings, and limitations.
- Validates summary structure using Pydantic.
- Checks that cited pages exist and contain text.
- Exports JSON data and readable Markdown reports.

## Technologies

Python, PyMuPDF, Pydantic, Codex CLI, pytest

## Setup

Clone the repository:

```bash
git clone https://github.com/amandat17/papertrail.git
cd papertrail
```

Create and activate a virtual environment on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Install the [Codex CLI](https://developers.openai.com/codex/cli)
and sign in before generating summaries. Summarization uses your
Codex account's usage allowance.

## Usage

Search arXiv, choose a result, and download and summarize the paper:

```bash
python main.py --query "human computer interaction"
```

Enter the result number when prompted, or enter `q` to cancel.

To search, download, and extract text without generating a summary:

```bash
python main.py --query 'ti:"Enabling Smartphone-based Estimation of Heart Rate"' --extract-only
```

To summarize a local PDF:

Create a `papers` folder and place a text-based PDF inside it.

```bash
mkdir -p papers
python main.py --pdf papers/sample.pdf
```

View available options:

```bash
python main.py --help
```

## Output

Results are saved in a folder named after the PDF:

```text
outputs/sample/
├── pages.json       # Extracted text and PDF page numbers
├── summary.json     # Structured summary
└── summary.md       # Readable report
```

For arXiv searches, the output folder uses the downloaded paper's arXiv ID,
and `source.json` also records its title, authors, links, and publication date.
The `--extract-only` option saves extracted text and available source metadata;
it does not generate new summary files.

Running the same PDF filename again overwrites its previous outputs
when successful.

## Tests

```bash
python -m pytest -q
```

Tests cover text extraction, page numbering, missing and blank PDFs,
and citation page validation. They do not call Codex.

## Limitations

- Scanned PDFs require OCR, which is not implemented.
- arXiv PDF downloads are limited to 25 MB.
- Serialized input text is limited to 60,000 characters.
- Complex PDF layouts may affect extraction quality.
- Citation checks validate page availability, not factual support.
- AI-generated claims should be checked against the original PDF.
