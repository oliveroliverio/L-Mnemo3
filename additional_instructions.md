# additional_instructions.md

## Primary Directive

The user is in a time crunch.

Claude should proceed with implementation immediately using the existing `PRD.md` as the source of truth.

Do **not** pause to ask for approval after proposing architecture.

Do **not** over-plan.

Do **not** wait for confirmation unless there is a truly blocking ambiguity that makes implementation impossible.

Make reasonable engineering assumptions and continue.

The goal is to get a working Screenshot → Raw Artifact → Derivative pipeline implemented as quickly and safely as possible.

---

# Scope

Only implement the scope described in `PRD.md`:

1. Screenshot → Raw Artifact pipeline
2. Raw Artifact → Derivative pipeline
3. Memory Peg decoration
4. Ollama/local LLM integration
5. SQLite-backed artifact storage
6. Markdown exports

Do not implement unrelated future features.

---

# Required External URLs

Use these values as defaults:

```python
MEMORY_PEG_BASE_URL = "http://100.88.124.124:3000/getCharacters"
OLLAMA_BASE_URL = "http://100.68.156.34:11434"
```

These should be configurable via environment variables, but the above values should work out of the box.

---

# Build-First Instruction

Claude should:

1. Inspect the current repository.
2. Identify the existing code structure.
3. Implement the smallest complete working version.
4. Run tests or sanity checks.
5. Commit changes atomically.
6. Continue to the next logical unit.

Avoid large speculative rewrites.

Prefer extending the existing codebase over replacing it.

---

# Atomic Git Commit Requirements

Claude must create small atomic commits.

Each commit should represent one logical change.

Examples:

```bash
git add <files>
git commit -m "feat: add memory peg client"
```

Good commit messages:

- feat: add memory peg client
- feat: add ollama client
- feat: add raw artifact schema
- feat: implement screenshot ingestion
- feat: build raw artifact from screenshots
- feat: generate derivatives from raw artifacts
- fix: handle empty llm response
- docs: add pipeline usage instructions
- test: add raw artifact builder tests

Bad commit messages:

- update stuff
- misc
- working
- huge implementation
- final version

---

# Commit Cadence

Commit after each completed logical unit.

Recommended sequence:

1. Confirm repo status
2. Add or update configuration
3. Commit
4. Add Memory Peg client
5. Commit
6. Add Ollama client
7. Commit
8. Add or update database schema
9. Commit
10. Add screenshot ingestion logic
11. Commit
12. Add raw artifact builder
13. Commit
14. Add derivative generator
15. Commit
16. Add CLI or command wiring
17. Commit
18. Add docs / usage instructions
19. Commit

Do not accumulate one giant uncommitted change.

---

# Implementation Bias

Prefer:

- Working code
- Simple Python modules
- SQLite
- Markdown exports
- Pydantic models where useful
- Clear logs
- Minimal dependencies
- Deterministic pipeline stages

Avoid:

- Multi-agent systems
- Complex orchestration
- Premature LangChain/LangGraph usage
- Giant refactors
- Large abstractions
- Blocking questions

---

# Agentic Framework Guidance

For v1, do **not** use LangChain, LangGraph, CrewAI, or AutoGen.

This pipeline does not require an agent framework yet.

Use direct service calls:

```text
Python → SQLite → Ollama → Markdown
```

Pydantic is acceptable and encouraged for structured data validation.

If structured LLM output becomes difficult, use Pydantic models plus retry/repair logic.

Only introduce PydanticAI if it clearly reduces complexity.

---

# Error Handling Requirements

Do not allow one failed screenshot or derivative to crash the entire pipeline.

Handle:

- Ollama unavailable
- Memory Peg API unavailable
- Empty LLM response
- Invalid JSON
- Corrupt screenshot
- Missing image path
- SQLite write failure

If Memory Peg lookup fails, continue with null peg fields and log a warning.

If Ollama fails, mark the artifact or derivative as failed and continue.

---

# Logging Requirements

Add useful logs for:

- Session start
- Screenshot ingestion
- LLM call start/end
- Raw artifact creation
- Memory Peg lookup
- Database writes
- Derivative generation
- Export paths

Logs should help the user debug the pipeline quickly.

---

# Testing / Sanity Checks

Run practical checks after implementation.

Examples:

```bash
python -m pytest
```

or, if no tests exist:

```bash
python -m compileall .
```

and a simple smoke test using a small screenshot set if available.

Do not skip validation entirely.

---

# Database Principle

SQLite is the source of truth.

Markdown files are exports.

Raw artifacts are canonical.

Derivatives are regenerable.

---

# Markdown Export Principle

Export:

```text
exports/raw_artifacts/
exports/derivatives/
exports/images/
```

Raw artifact markdown should include:

- title
- created datetime
- Memory Peg metadata
- source screenshot count
- extracted/cleaned learning content
- references to extracted images if present

Derivative markdown should include:

- source raw artifact id/title
- derivative type
- generated content
- created datetime

---

# Completion Criteria

Claude should stop only when there is a usable end-to-end version.

Minimum acceptable result:

1. Screenshots can be processed into a raw artifact.
2. Raw artifact is saved to SQLite.
3. Raw artifact is exported to Markdown.
4. Memory Peg metadata is attached.
5. Derivatives are generated from the raw artifact.
6. Derivatives are saved and exported.
7. Code is committed in atomic git commits.
8. Basic sanity checks pass.

---

# Final Response Expected From Claude

When done, Claude should provide:

1. Summary of implemented changes
2. List of commits created
3. Commands to run the pipeline
4. Any known limitations
5. Next recommended improvement

Keep the final response concise and practical.
