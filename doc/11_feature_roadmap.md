# OpenMedica - Feature Roadmap (OpenEvidence Trajectory)

This document serves as the long-term backlog for upgrading OpenMedica from its initial MVP into a robust, OpenEvidence-style medical AI platform. While data sources are limited to free/open-access APIs, the architecture and features will mimic enterprise clinical decision support systems.

Features here should be tackled sequentially after the core MVP in `01_current_state.md` (Phases 1-5) is completed.

## Phase 6: Clinical Evidence Expansion
OpenEvidence relies on high-quality, diverse clinical data. This phase expands our data limits.
- [ ] **Full-Text Ingestion (PMC)**: Upgrade `pubmed_fetcher.py` to pull open-access full-text articles from PubMed Central. Implement *Intelligent Chunking* (by abstract/methods/results) to prevent context bloat.
- [ ] **Evidence Hierarchy Filtering**: Add parameters to prioritize gold-standard evidence like *Systematic Reviews*, *Meta-Analyses*, and *Randomized Controlled Trials (RCTs)*.
- [ ] **Clinical Guidelines Integration (Stretch)**: Explore fetching open-access medical guidelines to ground answers not just in research, but in standard-of-care protocols.

## Phase 7: Clinical Search & RAG Architecture
OpenEvidence is known for its extreme accuracy. This phase upgrades the retrieval and generation pipeline.
- [ ] **Medical Query Expansion**: Use an LLM or MeSH (Medical Subject Headings) to expand user queries (e.g., mapping "Heart Attack" -> "Myocardial Infarction") before searching.
- [ ] **Hybrid Search with Re-ranking**: Combine ChromaDB's vector search (semantic) with BM25 keyword search (exact medical terminology), followed by a re-ranking step for optimal context precision.
- [ ] **Multi-Agent Verification Pipeline**: Utilize Pydantic AI to build a "Synthesizer Agent" and a strict "Reviewer Agent" to enforce the zero-hallucination constraint with extreme accuracy.

## Phase 8: OpenEvidence-Style UI & UX
Translating raw data into an easily digestible format for clinicians at the point of care.
- [ ] **PICO-Formatted Outputs**: Prompt the agent to structure complex clinical answers using the PICO framework (Population, Intervention, Comparison, Outcome) when applicable.
- [ ] **Evidence Grading UI**: Visually indicate the strength of the evidence (e.g., highlighting RCTs vs. Observational studies) next to the inline citations.
- [ ] **Conversational Memory & Filters**: Track chat history for follow-up questions, and add UI filters for publication date or study type.
- [ ] **Export & Share**: Allow users to export validated research summaries to PDF or clipboard for clinical notes.

## Phase 9: Evaluation & Safety
Proving that the system is safe and hallucination-free.
- [ ] **Automated RAG Evaluation**: Create a static test set of medical questions. Measure Context Precision and Faithfulness to scientifically prove zero-hallucinations before deploying complex updates.
- [ ] **User Feedback Loop**: Implement Thumbs Up/Down and reporting mechanisms in the Streamlit UI to log failures and improve the system.
