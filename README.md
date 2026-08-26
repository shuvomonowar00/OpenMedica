# OpenMedica

A zero-hallucination Medical RAG (Retrieval-Augmented Generation) pipeline that strictly grounds its answers in peer-reviewed PubMed literature.

## 🩺 Overview

OpenMedica is an open-source AI medical assistant designed to eliminate hallucinations common in standard LLMs. By combining the vast, peer-reviewed database of PubMed with a strict RAG pipeline built on Pydantic AI, OpenMedica ensures that every answer provided is factual, traceable, and grounded in real medical science.

## ✨ Key Features

- **Zero Hallucination Guarantee:** Enforced through strict output schemas via Pydantic AI.
- **PubMed Integration:** Directly fetches and indexes abstracts from the PubMed database.
- **Zero-Cost Infrastructure:** Built to run on free/open-source tools and generous free-tier APIs (e.g., Google AI Studio).
- **Separation of Concerns:** A clean, decoupled architecture with a FastAPI backend and a Streamlit frontend.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python, `uv` for package management.
- **Frontend:** Streamlit.
- **Data & RAG Engine:** Biopython (PubMed API), ChromaDB (Vector & Metadata Storage), Pydantic AI (Agent Framework).
- **AI Models:** Model-agnostic design (defaulting to Gemini 1.5 Flash/Pro and Gemini Embeddings via Google AI Studio).
- **Deployment:** Docker & Docker Compose.

## 📂 Project Structure

```text
OpenMedica/
├── backend/          # FastAPI server, data ingestion (PubMed), and RAG engine
├── frontend/         # Streamlit user interface
├── doc/              # Project documentation and architectural guidelines
└── docker-compose.yml# Container orchestration
```

## 🚀 Getting Started

*(Detailed setup instructions will be added as the project progresses through its development phases.)*

## 📜 License

This project is open-source and available under the MIT License.
