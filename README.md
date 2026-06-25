# L-Mnemo: Intelligent Learning Ingestion Pipeline

L-Mnemo is a state-of-the-art learning capture system designed to convert active study screenshots into structured, durable knowledge artifacts. Inspired by advanced ingestion workflows in frontier AI labs, it processes fragmented screenshots into coherent, annotated, and derivative-decorated study materials.

---

## 📖 Rationale & Goal
Modern learning occurs dynamically across multiple channels—Gemini/ChatGPT chat sessions, YouTube lectures, PDF whitepapers, and web-based documentation. Screenshots are the lowest-friction capture mechanism but are highly fragmented and lack structure. 

The goal of **L-Mnemo** is to ingest these screenshots via a streamlined frontend inbox, perform multimodal OCR/extraction using local VLMs (Vision-Language Models), group them into logical study sessions, and decorate them with contextual Memory Pegs. From there, it generates disposable, high-value learning derivatives (flashcards, summaries, and diagnostic review questions).

---

## 🛠️ Main Features
1. **Frontend Inbox (Next.js)**: A rapid-capture interface for markdown notes and images.
2. **Memory Peg Decoration**: Contextual metadata (weeks, days, quadrants, and character archetypes) acts as visual/spatial retrieval cues.
3. **Multimodal Extraction**: Invokes local VLMs (e.g., `qwen3-vl`) or external LLMs (e.g. DeepSeek) to perform OCR and extraction.
4. **SQLite Storage**: Local SQLite database integrity for structured queries.
5. **Downstream Derivatives**: Generates summaries, diagnostic questions, active recall flashcards, and knowledge gap reports.

---

## ⚙️ Installation & Setup

L-Mnemo consists of a Python CLI/Backend and a Next.js Frontend. 

### 1. Python Backend
The backend manages the SQLite database, local VLMs, and derivative processing.
```bash
# Ensure you have 'uv' installed
uv sync

# Activate the virtual environment
source .venv/bin/activate

# (Optional) Run CLI commands
python cli.py --help
```

### 2. Next.js Frontend
The frontend provides the inbox UI and connects to the ingestion APIs.
```bash
cd FRONTEND
npm install

# Set up your environment variables
cp .env.example .env.local
# Edit .env.local to include your NEXT_PUBLIC_MEMORY_PEG_API, NEXT_PUBLIC_SQLITE_API, and DEEPSEEK_API

# Start the development server
npm run dev
```
The frontend will be available at `http://localhost:3000`.

---

## 📊 Application Data Flow & Structures

The following diagram illustrates the data flow from the user's frontend interaction down to the database and derivative generation, highlighting the core data structures used.

```mermaid
graph TD
    %% Frontend Interaction
    User([User]) -->|Drafts Markdown & Attaches Images| UI[Frontend Inbox]
    
    %% API Integrations
    UI <-->|Fetch Metadata| MP_API[Memory Peg API]
    UI <-->|Chat/Extraction| LLM_API[DeepSeek LLM API]
    
    %% Payload Assembly
    UI -->|Assemble Payload| Payload{Artifact Payload}
    
    %% Backend Ingestion
    Payload -->|Submit POST| SQL_API[SQLite Ingestion API]
    SQL_API --> DB[(Local SQLite Database)]
    
    %% Python Backend Processing
    DB --> CLI[cli.py / Python Backend]
    CLI -->|Process| VLM[Local VLM OCR & Formatting]
    VLM --> Derivatives[Generate Derivatives: Flashcards, Quizzes, Summaries]
    Derivatives --> DB
    
    %% Data Structures (Notes)
    classDef type fill:#1e1e1e,stroke:#3b82f6,stroke-width:2px,color:#fff;
    
    subgraph Data Structures
        PegStruct[MemoryPegMetadata:<br/>- weekCreature<br/>- dayTheme<br/>- timeCharacter]
        PayloadStruct[ArtifactPayload:<br/>- markdown: string<br/>- images: string[]<br/>- datetime: string<br/>- quadrant: string<br/>- ...MemoryPegs]
    end
    
    MP_API -.->|Returns| PegStruct
    Payload -.->|Matches| PayloadStruct
    PegStruct:::type
    PayloadStruct:::type

    style User fill:#4F46E5,stroke:#312E81,stroke-width:2px,color:#fff
    style UI fill:#3B82F6,stroke:#1D4ED8,stroke-width:2px,color:#fff
    style DB fill:#059669,stroke:#065F46,stroke-width:2px,color:#fff
    style CLI fill:#10B981,stroke:#047857,stroke-width:2px,color:#fff
```

---

## 🔮 Roadmap Features
- **Mnemonic Scene Generation**: Combine extracted concepts with Memory Peg characters to build interactive visual memory scenes.
- **Flashcard Scheduling & Anki Integration**: Automate spaced-repetition sync.
- **RAG & Knowledge Graphs**: Allow semantic search over canonical raw artifacts.
- **Review Dashboard**: Provide a visual progress-tracking UI.
