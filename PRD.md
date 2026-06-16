# PRD.md — L-Mnemo Screenshot → Raw Artifact → Derivative Pipeline

## Project Overview

L-Mnemo is a learning capture system designed to transform study activity into durable knowledge artifacts.

The initial scope of this PRD is intentionally limited to:

1. Screenshot → Raw Artifact Pipeline
2. Raw Artifact → Derivative Pipeline

Future features (flashcard scheduling, knowledge graphs, memory palaces, chat capture, review systems, etc.) are out of scope.

---

# Product Goals

The user spends most learning time in:

- ChatGPT
- Gemini
- Claude
- YouTube
- Web pages
- PDFs
- Technical documentation

The system should:

- Capture learning activity automatically.
- Convert screenshots into coherent study notes.
- Generate higher-value derivative learning assets.
- Decorate artifacts with Memory Peg metadata.
- Store artifacts in a structured database.
- Remain simple and maintainable.

The architecture should resemble how OpenAI, Anthropic, Google, and other frontier AI organizations would build a multimodal knowledge ingestion pipeline.

---

# Design Philosophy

## What Big AI Labs Would Do

OpenAI, Anthropic, Google, and Meta would NOT:

- Store screenshots as the primary knowledge object.
- Create complex agent chains for every screenshot.
- Build a giant LangChain workflow for basic OCR.

Instead they would:

1. Capture source data.
2. Convert source data into structured text.
3. Group related content into coherent chunks.
4. Create canonical artifacts.
5. Generate downstream derivative assets.
6. Store everything in searchable databases.
7. Attach metadata for retrieval.

This PRD follows that philosophy.

---

# High-Level Architecture

```

Study Session
│
├── Screenshot Capture
│
├── Multimodal Extraction
│
├── Screenshot Grouping
│
├── Raw Artifact Generation
│
├── Memory Peg Decoration
│
├── Database Storage
│
└── Derivative Generation
    ├── Summary
    ├── Review Questions
    ├── Flashcards
    ├── Knowledge Gaps
    └── Future Derivatives

```

---

# External Services

## Memory Peg System

Used to decorate all knowledge artifacts.

```python
MEMORY_PEG_BASE_URL = "http://100.88.124.124:3000/getCharacters"
```

Expected response contains:

- Week character
- Day theme
- Time quadrant character
- Current datetime

Example:

```json
{
  "weekCharacter": {...},
  "dayTheme": {...},
  "timeCharacter": {...}
}
```

Purpose:

- Memory augmentation
- Retrieval cues
- Knowledge palace decoration

---

## Local LLM Service

```python
OLLAMA_BASE_URL = "http://100.68.156.34:11434"
```

Primary use:

- OCR extraction
- Screenshot understanding
- Raw artifact generation
- Derivative generation

Recommended models:

### Vision

- qwen3-vl:30b
- qwen3-vl:8b

### Text

- deepseek-r1:70b
- qwen3-coder:30b

---

# Screenshot → Raw Artifact Pipeline

## Goal

Convert many screenshots into one coherent study artifact.

---

## Session Lifecycle

### Start Session

User initiates:

```

mnemo start-session

```

Create:

```

study_session

```

record.

Store:

- session_id
- title
- topic
- category
- start_time

---

## Screenshot Capture

Current trigger methods:

- Snagit
- Hotkeys
- Clipboard ingestion

Each screenshot stored:

```

screenshots/

```

Metadata:

```json
{
  "session_id": 12,
  "timestamp": "...",
  "filepath": "..."
}
```

---

## Screenshot Grouping

Important:

Screenshots are NOT knowledge.

Screenshots are merely source material.

System should group screenshots into logical chunks.

Example:

23 screenshots from CIS101 Chapter 1

Become:

```

Raw Artifact:
"CIS101 Chapter 1 - Fundamentals"

```

Grouping signals:

- Temporal proximity
- Same session
- Similar content
- Similar embeddings (future)

Initial implementation:

Session-based grouping.

---

## Multimodal Extraction

Each screenshot sent to local VLM.

Prompt responsibilities:

- OCR text
- Extract tables
- Extract diagrams
- Extract code
- Extract formulas
- Extract educational meaning

Output:

Structured markdown fragments.

Example:

```markdown
## Ethical Mindset

An ethical mindset is...
```

---

## Image Handling

Important principle:

DO NOT ask the LLM to recreate diagrams.

Instead:

1. Extract original images from screenshots.
2. Store images separately.
3. Reference images in markdown.

Reason:

Prevents hallucination.
Preserves original educational material.

---

## Raw Artifact Generation

Raw Artifact is the canonical source document.

Example:

```

raw_artifact

```

contains:

- merged OCR text
- merged explanations
- extracted figures
- source references

Output:

```markdown
# CIS101 Chapter 1

...
```

---

# Memory Peg Decoration

Before saving artifact:

Call:

```

GET MEMORY_PEG_BASE_URL

```

Store:

### Datetime

- currentDate

### Week

- week number
- week character

### Day

- weekday
- theme
- props

### Time

- quadrant
- time character

Attach to artifact metadata.

Example:

```json
{
  "week_character": "Buzz Lightyear",
  "day_theme": "Independence Day",
  "time_character": "Bill Nye"
}
```

---

# Storage Layer

## SQLite (Initial)

Tables:

### study_sessions

Tracks session metadata.

### screenshots

Tracks image sources.

### raw_artifacts

Canonical learning documents.

### artifact_images

Stores extracted images.

---

Raw Artifact Schema

```sql
id
session_id
title
markdown
created_at

week_character
day_theme
time_character

week_number
weekday

source_screenshot_count
```

---

# Raw Artifact → Derivative Pipeline

## Goal

Generate study-friendly assets from canonical artifacts.

Raw Artifact remains source of truth.

Derivatives are disposable and regenerable.

---

## Trigger

When session closes:

```

mnemo end-session

```

Background job executes:

```

process_derivatives.py

```

---

# Derivative Types

## Summary

Purpose:

Condense content.

Output:

```markdown
# Summary
...
```

---

## Review Questions

Purpose:

Active recall.

Output:

```markdown
# Review Questions
1.
2.
3.
```

---

## Flashcards

Purpose:

Spaced repetition.

Output:

```markdown
Q:
A:
```

---

## Knowledge Gaps

Purpose:

Identify weak understanding areas.

Output:

```markdown
# Concepts Requiring Clarification
...
```

---

## Mnemonic Enhancement (Future)

Use Memory Peg metadata.

Example:

Week Character:

Buzz Lightyear

Time Character:

Bill Nye

Generate memory scenes connecting concepts to peg characters.

Future feature.

Not required in v1.

---

# Recommended Architecture

## v1

No Agent Framework

Simple pipeline:

```

Python
→ SQLite
→ Ollama
→ Markdown

```

Advantages:

- Easy debugging
- Fast development
- Minimal complexity

---

## v2

Introduce PydanticAI

Reasons:

- Strong structured outputs
- Type safety
- Validation
- Cleaner prompts

Recommended over LangChain initially.

---

## v3

Optional LangGraph

Only if:

- Multi-agent workflows emerge
- Planning becomes necessary
- Human-in-loop review added

Avoid premature complexity.

---

# Directory Structure

```

mnemo/

    capture/
        screenshot_capture.py

    ingestion/
        process_screenshots.py

    artifacts/
        build_raw_artifact.py

    derivatives/
        process_derivatives.py

    memory_peg/
        memory_peg_client.py

    llm/
        ollama_client.py

    db/
        sqlite.py

exports/

    raw_artifacts/
    derivatives/
    images/

```

---

# Non-Goals

Not part of this PRD:

- Knowledge graph
- RAG search
- Agent swarms
- Multi-agent orchestration
- Flashcard scheduling
- Anki sync
- Chat capture
- Memory palace image generation
- Review dashboard

These belong in future PRDs.

---

# Success Criteria

A user can:

1. Start study session.
2. Take screenshots while learning.
3. End study session.
4. Receive one clean Raw Artifact.
5. Receive derivative study materials.
6. Have all artifacts decorated with Memory Peg metadata.
7. Store everything in SQLite and Markdown.
8. Regenerate derivatives at any time.

The system should remain simple, deterministic, debuggable, and extensible.
