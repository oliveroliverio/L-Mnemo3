# LOG.md

## 2026-06-16

### CHORE: configure gitignore, add readme, and document setup
- **Files Changed**:
  - [.gitignore](file:///Users/mbp-14/CLONED/L-Mnemo3/.gitignore): Added comprehensive ignores for Node.js, Python, SQLite databases, OS metadata, and build exports.
  - [README.md](file:///Users/mbp-14/CLONED/L-Mnemo3/README.md): Created the initial project README containing rationale, scope, features, roadmap, and a data-flow Mermaid diagram.
  - [@Docs/Gitignore-Setup.md](file:///Users/mbp-14/CLONED/L-Mnemo3/@Docs/Gitignore-Setup.md): Added step-by-step instructions on the gitignore configuration, fulfilling the agent panel documentation requirement.
- **Why**:
  - Configured project environment boilerplate to prevent unwanted temporary or environment files from being tracked.
  - Documented setup and pipeline architecture visually to orient developer workflow.

## FEAT: Scaffold L-Mnemo3 Frontend Application
- Scaffolded Next.js 15 application with React 19, TypeScript, TailwindCSS, and shadcn/ui.
- Created `FRONTEND/app/page.tsx` with a 3-column layout.
- Added `FRONTEND/components/layout/LeftSidebar.tsx` to display Memory Peg data and quadrant countdown.
- Added `FRONTEND/components/layout/CenterWorkspace.tsx` to serve as the drag-and-drop Markdown editor.
- Added `FRONTEND/components/layout/RightSidebar.tsx` for draft statistics and image attachments.
- Added `FRONTEND/components/layout/BottomToolbar.tsx` for draft actions and manual submission.
- Added Zustand store in `FRONTEND/store/useAppStore.ts` with `localStorage` persistence for autosave and draft recovery.
- Added `FRONTEND/hooks/useMemoryPeg.ts` to poll Memory Peg API every 60 seconds.
- Added `FRONTEND/hooks/useQuadrantTimer.ts` for automatic 15-minute quadrant submissions.
- Created `FRONTEND/.env.example` to provide required API placeholders.
- Updated `FRONTEND/README.md` with project logic and mermaid architecture.

## [BUGFIX & FEAT] Fix Memory Peg API Integration and Add LLM Service
**Date:** 2026-06-25

**Changes:**
- **BUGFIX (CORS)**: Configured Next.js rewrites in `next.config.ts` to proxy requests to `NEXT_PUBLIC_MEMORY_PEG_API` and `NEXT_PUBLIC_SQLITE_API` to bypass browser CORS policies. Updated `MemoryPegService.ts` and `SubmissionService.ts` to use these local rewrite endpoints.
- **BUGFIX (React Error)**: Updated `MemoryPegMetadata` type in `types/index.ts` to correctly mirror the nested JSON structure returned by the Memory Peg API. Updated `LeftSidebar.tsx` and `useSubmission.ts` to extract string properties (e.g., `dayTheme.theme`) instead of rendering whole objects.
- **FEAT (LLM API)**: Installed `openai` SDK. Created `app/api/llm/route.ts` to securely proxy requests to the DeepSeek API using the `DEEPSEEK_API` environment variable. Added `LLMService.ts` for the frontend to interact with this route.
- **CHORE (VS Code)**: Created `.vscode/settings.json` and enabled `python.terminal.useEnvFile` to fix terminal warnings regarding environment injection.

**Files Changed:**
- `FRONTEND/next.config.ts`: Added proxy rewrites and `allowedDevOrigins` for HMR.
- `FRONTEND/services/MemoryPegService.ts`: Switched URL to local API rewrite.
- `FRONTEND/services/SubmissionService.ts`: Switched URL to local API rewrite.
- `FRONTEND/types/index.ts`: Updated `MemoryPegMetadata` interface.
- `FRONTEND/components/layout/LeftSidebar.tsx`: Fixed rendering of nested object properties.
- `FRONTEND/hooks/useSubmission.ts`: Fixed extraction of object properties.
- `FRONTEND/app/api/llm/route.ts`: New backend route for DeepSeek.
- `FRONTEND/services/LLMService.ts`: New frontend service for LLM integration.
- `.vscode/settings.json`: Added Python extension config.

**Terminal Commands Executed:**
```bash
mkdir -p ../.vscode
npm install openai
mkdir -p app/api/llm
```
