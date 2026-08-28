# OpenMedica - Commands Reference & Cheat Sheet

This document contains all the necessary commands to run, test, and manage the OpenMedica platform. Copy and paste these directly into your terminal.

> **Note on `uv`:** We use `uv` as our lightning-fast package manager. Using `uv run` ensures that the command executes securely inside the isolated virtual environment (`.venv`) for that specific folder.

---

## 1. Local Development (Native)

For rapid development with instant hot-reloading. You will need **two separate terminal windows**.

### Start the Backend API (Terminal 1)
```bash
cd backend
uv run uvicorn main:app --reload
```
*(The API will be available at `http://localhost:8000`)*

> **Alternative Backend Command**: Because we use `python-dotenv` in our code, the `.env` file is loaded automatically. However, if you ever remove `python-dotenv`, you must manually pass the path to the environment file like this:
> ```bash
> uv run uvicorn main:app --reload --env-file ../.env
> ```

### Start the Streamlit Frontend UI (Terminal 2)
*(Note: As we plan to add a Next.js frontend in the future, this specifies the Streamlit MVP)*
```bash
cd frontend
uv run streamlit run app.py
```
*(The UI will automatically open in your browser at `http://localhost:8501`)*

---

## 2. Automated Testing

Always run tests before pushing code to ensure zero regressions.

### Run Backend Tests
```bash
cd backend
uv run pytest tests/
```

### Run Streamlit Frontend Tests
```bash
cd frontend
uv run pytest tests/
```

---

## 3. Docker (Production Simulation)

Use Docker Compose when you want to spin up both the frontend and backend in isolated, production-ready containers. 

*Run these commands from the **root** folder (`OpenMedica/`).*

### Build and Start All Containers
```bash
docker-compose up --build
```
*(You can access the UI at `http://localhost:8501` just like local dev).*

### Run Containers in the Background (Detached Mode)
```bash
docker-compose up -d --build
```

### Stop All Containers
```bash
docker-compose down
```

---

## 4. Dependency Management (`uv`)

If you need to add new Python libraries to either the frontend or backend in the future, navigate into the respective folder (`cd backend` or `cd frontend`) and use these commands:

### Add a Standard Package
```bash
uv add <package_name>
# Example: uv add pandas
```

### Add a Development-Only Package (like testing tools)
```bash
uv add --dev <package_name>
# Example: uv add --dev pytest
```

### Remove a Package
```bash
uv remove <package_name>
```
