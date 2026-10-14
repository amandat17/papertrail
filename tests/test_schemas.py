import pytest

from schemas import Finding, PaperSummary, validate_references


def make_summary(page_numbers):
    # Build a small example summary for testing citations.
    return PaperSummary(
        overview="An example research summary.",
        methods=["An example method."],
        findings=[
            Finding(
                claim="An example finding.",
                pages=page_numbers,
            )
        ],
        limitations=[],
    )


def test_valid_page_reference_is_accepted():
    pages = [{"page": 1, "text": "Supporting text."}]

    # This should finish without raising an error.
    validate_references(make_summary([1]), pages)


def test_nonexistent_page_reference_is_rejected():
    pages = [{"page": 1, "text": "Supporting text."}]

    # Page 2 does not exist in the supplied pages.
    with pytest.raises(ValueError):
        validate_references(make_summary([2]), pages)


def test_empty_page_reference_is_rejected():
    pages = [{"page": 1, "text": "   "}]

    # A page with no readable text should not be accepted as a citation.
    with pytest.raises(ValueError):
        validate_references(make_summary([1]), pages)


def test_finding_without_references_is_rejected():
    pages = [{"page": 1, "text": "Supporting text."}]

    with pytest.raises(ValueError):
        validate_references(make_summary([]), pages)