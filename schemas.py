from pydantic import BaseModel, ConfigDict

#Represents one finding and the PDF pages cited as evidence
#BaseModel provides Pydantic's data validation
class Finding(BaseModel):
    #Reject unexpected fields that are not defined below
    model_config = ConfigDict(extra="forbid")

    #The finding, written as text
    claim: str
    #Supporting PDF page numbers 2 and 3, such as [2,3]
    pages: list[int]

#Defines the required structure of the complete research summary
class PaperSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Short explanation of the paper
    overview: str
    # Research methods used by the authors
    methods: list[str]
    # Findings with supporting page references
    findings: list[Finding]
    # Limitations stated by the authors
    limitations: list[str]


def validate_references(
    summary: PaperSummary,
    pages: list[dict],
) -> None:
    """
    Check for empty claims and invalid page references.

    Each extracted page is a dictionary:
    {"page":1,"text":"Extracted text..."}

    Returns nothing on success; raise ValueError on failure.
    This does not verify whether the cited text supports a claim
    """

    # Build a set of page numbers that contain extracted text
    # strip () removes surrounding whitespace; an empty string is false
    valid_pages = {
        page["page"]
        for page in pages
        if page["text"].strip()
    }

    # A string can pass Pydantic validation but still be blank
    if not summary.overview.strip():
        raise ValueError("The summary overview is empty")

    # Check each finding individually
    for finding in summary.findings:
        # Reject claims that are empty or contain only whitespace
        if not finding.claim.strip():
            raise ValueError("A finding contains an empty claim")

        # Require at least one supporting page reference
        if not finding.pages:
            raise ValueError("A finding has no page references")

        # Every cited page must exist and contain extracted text
        # issubset() checks that all cited numbers are in valid_pages
        if not set(finding.pages).issubset(valid_pages):
            raise ValueError("A finding cites a missing or empty PDF page")

