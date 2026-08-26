# OpenMedica - Clean Coding Guidelines

All AI agents and developers MUST strictly follow these guidelines when writing or modifying code for this project.

## 1. General Python Standards
- **Strict Type Hinting**: All functions, arguments, and return types must be strictly type-hinted. 
- **Docstrings**: Every function, class, and module must have a concise docstring explaining its purpose.
- **Error Handling**: Do not fail silently. Catch specific exceptions and log them, or raise appropriate application errors.
- **Modularity (DRY)**: Functions should do exactly one thing. If a function is too long or complex, break it down into smaller helper functions.

## 2. Backend Rules (FastAPI & Data)
- **Strict Schemas (Pydantic)**: Always use Pydantic `BaseModel` classes for API request payloads and response outputs. Never use raw unstructured dictionaries for data validation.
- **Thin Routers**: API endpoint functions in `main.py` (or router files) should be thin. Heavy business logic, database queries, and AI orchestration must be separated into modular service files (e.g., inside a `services/` or `core/` folder).
- **Graceful Exceptions**: Use FastAPI's `HTTPException` to handle client/server errors and return proper HTTP status codes.
- **Async Programming**: Use `async def` for endpoints and functions that perform network or disk IO (e.g., database queries, calling the PubMed API, or interacting with LLMs).

## 3. Frontend Rules (Streamlit UI)
- **Zero Database/AI Logic**: The Streamlit frontend must NEVER connect directly to ChromaDB, the LLM, or PubMed. All data fetching and AI processing must be done via REST API calls to the backend using the `requests` library.
- **Component Modularity**: Break down complex UI sections into separate rendering functions (e.g., `render_sidebar()`, `render_chat_interface()`) rather than writing one massive script.
- **State Management**: Use `st.session_state` deliberately. Clearly initialize all session state variables at the very top of your script before they are used to prevent `KeyError` crashes.
