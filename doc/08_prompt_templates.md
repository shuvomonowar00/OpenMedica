# AI Prompt Templates

Use these copy-paste templates to start new chat sessions for specific tasks. Simply fill in the brackets [...] with your specific needs.

## 0. Master Project Context (For Web UIs or External Agents)
*Use this prompt when starting a completely new session in a standard web browser UI (like ChatGPT, Claude, or Gemini Web) where the AI cannot automatically read your local project files. This gives them the complete mental model of OpenMedica instantly.*

> "Act as a Senior AI Software Engineer and Project Manager. We are building **OpenMedica**, an advanced medical AI platform (following an OpenEvidence-style trajectory). Our goal is to provide zero-hallucination medical answers strictly grounded in peer-reviewed literature (PubMed/PMC).
> 
> **Core Architecture & Tech Stack:**
> - **Frontend (UI):** Streamlit (Chat interface, PICO-formatted data display, Evidence grading UI).
> - **Backend (API):** FastAPI (REST endpoints, data ingestion).
> - **RAG & Search:** Hybrid Search (ChromaDB for semantic + BM25 for keyword matching).
> - **AI Engine:** Pydantic AI driving a Multi-Agent System (a Synthesizer Agent to draft answers in PICO format, and a strict Reviewer Agent to enforce zero hallucinations).
> - **Dependency Management:** `uv` and Docker.
> 
> **Strict Rules:**
> 1. ZERO HALLUCINATION: All medical claims must be explicitly grounded in provided evidence.
> 2. ARCHITECTURE: Never mix frontend UI code with backend data logic.
> 
> Before we begin, please ask me to paste the contents of `doc/01_current_state.md` so you know exactly what task we are working on today."

## 1. General Task Continuation
Use this when you just want the AI (inside an IDE like Cursor/Antigravity) to pick up exactly where it left off.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. Please silently read doc/01_current_state.md to understand our progress, and then begin executing the very next uncompleted task in the current phase."

## 2. Code Implementation (Specific Feature)
Use this when you want to build a specific file or feature.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. Please silently read doc/01_current_state.md. Our current task is to implement the [Backend/Frontend] feature for [Feature Name, e.g., PubMed API Fetcher]. Please write the code, ensuring it strictly follows our zero-hallucination architecture. When finished, update 01_current_state.md."

## 3. Planning & Architecture
Use this when designing a new feature, pivoting, or solving a complex logic problem *before* writing code.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. We need to design the architecture for a new feature: [Describe Feature]. Please read doc/02_architecture.md and doc/04_business_mvp.md for context. Do NOT write code yet. Provide a step-by-step implementation plan and outline any updates needed for our architecture docs."

## 4. Debugging & Error Fixing
Use this when you hit a bug and need a quick fix without losing token context.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. I am encountering an error when running [File or Command Name]. Here is the error log: 
> \\\
> [Paste Error Log Here]
> \\\
> Please analyze this error and provide the fix. You can read doc/02_architecture.md if you need context on how this component fits into the system."

## 5. Testing & QA
Use this to ensure your medical app remains hallucination-free and stable.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. We need to write tests for [Target File/Component, e.g., backend/rag_engine.py]. Please review doc/06_testing_and_evals.md for our QA protocols. Create robust automated tests in the tests/ folder. Ensure you test for edge cases like [Specific Edge Case, e.g., empty API responses]."

## 6. Deployment & DevOps
Use this when you are ready to push the code to a server.
> "We are working on OpenMedica. Your background instructions are in GEMINI.md. We are preparing for deployment to [Target Platform, e.g., Docker / Google Cloud]. Please read doc/07_deployment.md for context. Generate the necessary configuration files and provide a step-by-step deployment runbook."
