# Product Requirements Document

# Project

L-Mnemo3 Frontend

Location:

FRONTEND/

This project is the frontend interface for L-Mnemo3.

The frontend will eventually communicate with multiple backend AI services.

Primary backend:
- Memory Peg API
- LLM API
- SQLite ingestion API

The frontend itself should be completely modern, responsive, modular, and easy to extend.

---

# Tech Stack

Use:

- Next.js 15
- React 19
- TypeScript
- TailwindCSS
- shadcn/ui
- React Hook Form
- Zod
- TanStack Query
- Zustand
- Framer Motion
- Lucide Icons

Use the App Router.

Use functional components.

Strict TypeScript.

No class components.

Organize using feature-based folders.

---

# Environment Variables

Create a .env.local

Example:

MEMORY_PEG_API=http://100.88.124.124:3000

Future variables:

LLM_API=
SQLITE_API=
OPENAI_API_KEY=
OLLAMA_API=

Never hardcode URLs.

---

# Purpose

The application is essentially an "inbox."

The user continuously collects information throughout the day.

Every fixed 15-minute memory quadrant, everything currently inside the inbox is submitted as one RAW artifact.

That artifact becomes decorated using the Memory Peg System.

Nothing should be summarized by the frontend.

The frontend simply packages the raw content and metadata.

---

# Memory Peg Integration

Use

GET

${MEMORY_PEG_API}/getCharacters

This endpoint returns something similar to:

{
  dayTheme,
  weekCharacter,
  timeCharacter,
  quadrant,
  datetime,
  ...
}

These values are considered authoritative.

Never calculate them in the frontend.

Always fetch them from the API.

The frontend should refresh these values every 60 seconds.

The UI should always display:

Current Day Theme

Current Week Creature

Current Time Character

Current Quadrant

Current Datetime

The UI should clearly show the user what memory location is currently active.

---

# Layout

Three-column responsive layout.

Left Sidebar

Center Workspace

Right Sidebar

---

# Left Sidebar

Contains:

Current Memory Peg card

Day Theme

Week Creature

Time Character

Current Time

Quadrant countdown

Next submission countdown

Today's artifact count

Quick statistics

Settings

---

# Center Workspace

Large markdown editor.

Supports:

Plain text

Markdown

Copy/Paste

Drag-and-drop images

Paste screenshots

Multiple images

Image preview

Remove images

Reorder images

Autosave locally.

No character limit.

Editor should feel similar to Obsidian or Notion.

---

# Right Sidebar

Shows:

Current attached images

Metadata preview

Estimated token count

Markdown statistics

Word count

Character count

Reading time

Current datetime decoration

Pending submission preview

---

# Bottom Toolbar

Contains

Submit Now

Clear

Undo

Redo

Insert Timestamp

Insert Divider

Paste from Clipboard

Toggle Preview

Settings

---

# Submission Logic

Every fixed 15 minutes:

Automatically gather:

Current markdown

Current images

Current datetime

Memory Peg metadata

Package into one payload.

Example:

{
    markdown,
    images,
    datetime,
    quadrant,
    weekCharacter,
    timeCharacter,
    dayTheme
}

Send to backend ingestion API.

Do not perform AI summarization.

Do not modify user text.

Treat everything as immutable RAW data.

After successful submission:

Clear workspace.

Keep autosave history.

Show success notification.

---

# Manual Submission

The user may press Submit Now.

The exact same payload is created.

The only difference is:

manual=true

---

# Draft Recovery

If browser closes:

Restore editor

Restore images

Restore cursor

Restore scroll

Restore draft

---

# Autosave

Every 5 seconds.

Save locally.

Never lose user work.

---

# Image Handling

Support:

Clipboard paste

Drag/drop

File picker

PNG

JPEG

WEBP

GIF

Display thumbnails.

Allow deleting individual images.

Allow drag reordering.

---

# Markdown Support

Support:

Headers

Tables

Task Lists

Code blocks

Inline code

Quotes

Math

Links

Images

Horizontal rules

---

# Countdown

Display

Current quadrant countdown.

Example

08:12 remaining

Automatically update every second.

When countdown reaches zero:

Perform submission.

Refresh Memory Peg metadata.

Begin next countdown.

---

# Notifications

Toast notifications.

Examples

Draft Saved

Submission Successful

Submission Failed

Memory Peg Connected

Memory Peg Offline

Recovered Draft

---

# Connection Status

Show connection indicators.

Memory Peg API

Backend API

LLM API

SQLite API

Green

Yellow

Red

---

# Error Handling

If Memory Peg API is unreachable:

Retry every 30 seconds.

Display warning.

Prevent automatic submission until metadata is available.

Allow manual retry.

---

# Accessibility

Keyboard shortcuts.

Tab navigation.

Screen reader labels.

Dark mode.

Light mode.

Responsive.

---

# UI Style

Modern.

Minimal.

Clean.

Large comfortable spacing.

Rounded corners.

Subtle animations.

No excessive colors.

Inspired by:

Obsidian

Linear

Raycast

Notion

Cursor

---

# Folder Structure

app/

components/

features/

hooks/

lib/

services/

store/

types/

utils/

styles/

public/

---

# Services

Create services for

MemoryPegService

SubmissionService

DraftService

CountdownService

ImageService

SettingsService

---

# State Management

Use Zustand.

Global state should include:

Current Memory Peg metadata

Current draft

Images

Submission queue

Settings

Connection status

Countdown

---

# Future Features (Do Not Implement Yet)

Authentication

Multiple notebooks

Search

SQLite browser

Artifact history

Flashcards

Review generation

Embeddings

Semantic search

OCR

Speech-to-text

Offline synchronization

Electron desktop app

Tauri desktop app

PWA support

Voice dictation

Multiple AI providers

Background upload queue

Artifact timeline

Daily review

Weekly review

Memory Palace visualization

---

# Development Guidelines

Write clean, modular code.

Prefer reusable components.

Avoid duplicate logic.

Use custom hooks.

Strong TypeScript types.

No inline styles.

No unnecessary dependencies.

Keep components under approximately 250 lines when practical.

Document all major components.

Follow modern React best practices.

The resulting application should feel production-ready, highly extensible, and capable of scaling into the primary frontend for the L-Mnemo ecosystem.