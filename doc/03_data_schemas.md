# Data Schemas

These core Pydantic schemas define the data structures flowing through our RAG pipeline, ensuring strict type safety and zero-hallucination validation.

## 1. Article Schema
Represents a fetched piece of evidence from PubMed/PMC.
```python
class ArticleSchema(BaseModel):
    pmid: str
    title: str
    authors: list[str]
    publication_year: int
    abstract: str
    full_text: str | None = None
    study_type: str  # e.g., "RCT", "Meta-Analysis", "Observational"
    evidence_level: int  # e.g., 1 for Meta-Analysis, 2 for RCT, etc.
```

## 2. Query Expansion Schema
Used by the LLM to structure expanded queries before searching.
```python
class QueryExpansionSchema(BaseModel):
    original_query: str
    mesh_terms: list[str]
    expanded_search_queries: list[str]
```

## 3. PICO Answer Schema
The strict output format required from the Synthesizer Agent.
```python
class CitationSchema(BaseModel):
    pmid: str
    inline_reference: str  # e.g., "[1]"
    evidence_grade: str  # e.g., "RCT"

class PICOAnswerSchema(BaseModel):
    population: str | None = Field(description="The target patient population")
    intervention: str | None = Field(description="The treatment, test, or exposure")
    comparison: str | None = Field(description="The alternative or control")
    outcome: str | None = Field(description="The clinical outcome or result")
    general_summary: str = Field(description="A cohesive summary of the findings")
    citations_used: list[CitationSchema]
```
