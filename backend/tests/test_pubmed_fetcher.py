import pytest
from unittest.mock import patch
from services.pubmed_fetcher import _parse_pmc_xml, _sync_fetch_articles

def test_parse_pmc_xml():
    dummy_xml = b"""
    <article>
        <body>
            <sec>
                <title>Introduction</title>
                <p>This is the <b>intro</b>.</p>
                <p>More intro text.</p>
            </sec>
            <sec>
                <title>Methods</title>
                <p>We did a <xref>test</xref>.</p>
            </sec>
        </body>
    </article>
    """
    
    sections = _parse_pmc_xml(dummy_xml)
    
    assert len(sections) == 2
    
    assert sections[0].section_title == "Introduction"
    assert "This is the intro." in sections[0].content
    assert "More intro text." in sections[0].content
    
    assert sections[1].section_title == "Methods"
    assert "We did a test." in sections[1].content

@patch("services.pubmed_fetcher.Entrez.esearch")
@patch("services.pubmed_fetcher.Entrez.read")
@patch("services.pubmed_fetcher.Entrez.efetch")
def test_sync_fetch_articles_high_evidence(mock_efetch, mock_read, mock_esearch):
    # Setup mock returns to prevent failures when trying to iterate
    mock_read.return_value = {"IdList": []} # simulate empty results to exit early
    
    # Call the function with high_evidence_only=True
    _sync_fetch_articles(topic="Cancer", max_results=1, high_evidence_only=True)
    
    # Assert that esearch was called with the correct filter appended
    mock_esearch.assert_called_once()
    called_args, called_kwargs = mock_esearch.call_args
    assert called_kwargs["db"] == "pubmed"
    expected_term = 'Cancer AND ("Meta-Analysis"[Publication Type] OR "Randomized Controlled Trial"[Publication Type] OR "Systematic Review"[Publication Type])'
    assert called_kwargs["term"] == expected_term

@patch("services.pubmed_fetcher.Entrez.esearch")
@patch("services.pubmed_fetcher.Entrez.read")
@patch("services.pubmed_fetcher.Entrez.efetch")
def test_sync_fetch_articles_normal(mock_efetch, mock_read, mock_esearch):
    mock_read.return_value = {"IdList": []}
    
    # Call the function with high_evidence_only=False
    _sync_fetch_articles(topic="Diabetes", max_results=1, high_evidence_only=False)
    
    # Assert that esearch was called without the filter
    mock_esearch.assert_called_once()
    _, called_kwargs = mock_esearch.call_args
    assert called_kwargs["term"] == "Diabetes"
