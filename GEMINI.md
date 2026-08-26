# OpenMedica AI Assistant Rules

You are an AI coding assistant working on the OpenMedica project. 

## Initialization Required
Every time you start a new session or are asked a question, you MUST silently read the following files before taking action:
1. doc/00_agent_init.md (for core rules and constraints)
2. doc/09_tech_stack.md (for the strict list of authorized libraries)
3. doc/01_current_state.md (to understand what phase we are in and what the current task is)

## Strict Constraints
- NEVER hallucinate medical data.
- NEVER mix frontend and backend code. Use the rontend/ and ackend/ directories strictly.
- Always output clean, modular Python code based ONLY on the approved tech stack in 09_tech_stack.md.
- Update doc/01_current_state.md automatically when you complete a task.

Do not read other markdown files in the doc/ folder unless the current task explicitly requires it (to save context tokens).
