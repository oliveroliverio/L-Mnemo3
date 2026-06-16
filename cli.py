#!/usr/bin/env python3
"""
mnemo CLI — Learning Ingestion Pipeline

Usage:
    python cli.py start-session --title "CIS101 Chapter 1" [--topic "OS Basics"] [--category "CIS"]
    python cli.py add-screenshot path/to/screenshot.png [--session <id>]
    python cli.py end-session [--session <id>] [--title "Override title"]
    python cli.py regen-derivatives <artifact_id>
    python cli.py list-artifacts
    python cli.py show-session [--session <id>]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import config
from mnemo.db import sqlite as db
from mnemo.capture.screenshot_capture import add_screenshot
from mnemo.ingestion.process_screenshots import process_session_screenshots
from mnemo.artifacts.build_raw_artifact import build_raw_artifact, export_raw_artifact
from mnemo.derivatives.process_derivatives import process_all_derivatives, export_all_derivatives

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mnemo.cli")


# ── Active session helpers ─────────────────────────────────────────────────────

def _save_active_session(session_id: int) -> None:
    Path(config.ACTIVE_SESSION_FILE).write_text(str(session_id))


def _load_active_session() -> int | None:
    p = Path(config.ACTIVE_SESSION_FILE)
    if not p.exists():
        return None
    try:
        return int(p.read_text().strip())
    except ValueError:
        return None


def _clear_active_session() -> None:
    p = Path(config.ACTIVE_SESSION_FILE)
    if p.exists():
        p.unlink()


def _resolve_session(args_session: int | None) -> int:
    if args_session:
        return args_session
    session_id = _load_active_session()
    if session_id is None:
        print("ERROR: No active session. Run `start-session` first or pass --session <id>.")
        sys.exit(1)
    return session_id


# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_start_session(args: argparse.Namespace) -> None:
    db.init_db()
    session_id = db.create_session(
        title=args.title,
        topic=args.topic or "",
        category=args.category or "",
    )
    _save_active_session(session_id)
    print(f"Session started: id={session_id}  title={args.title!r}")
    print(f"Active session saved to {config.ACTIVE_SESSION_FILE}")
    print(f"\nNext: take screenshots, then run:")
    print(f"  python cli.py add-screenshot path/to/shot.png")
    print(f"  python cli.py end-session")


def cmd_add_screenshot(args: argparse.Namespace) -> None:
    db.init_db()
    session_id = _resolve_session(args.session)
    for filepath in args.paths:
        screenshot_id = add_screenshot(session_id, filepath, copy_to_dir=True)
        print(f"Screenshot added: id={screenshot_id}  path={filepath}")


def cmd_end_session(args: argparse.Namespace) -> None:
    db.init_db()
    session_id = _resolve_session(args.session)

    session = db.get_session(session_id)
    if not session:
        print(f"ERROR: Session {session_id} not found")
        sys.exit(1)

    print(f"\n[1/5] Ending session {session_id}: {session['title']!r}")
    db.end_session(session_id)

    print("[2/5] Processing screenshots via VLM…")
    counts = process_session_screenshots(session_id)
    print(f"      Screenshots: {counts['processed']} processed, {counts['failed']} failed of {counts['total']} total")

    if counts["processed"] == 0:
        print("ERROR: No screenshots were processed. Cannot build artifact.")
        sys.exit(1)

    print("[3/5] Building raw artifact…")
    title = args.title or session["title"]
    artifact_id = build_raw_artifact(session_id, title=title)
    artifact_path = export_raw_artifact(artifact_id)
    print(f"      Raw artifact saved: id={artifact_id}")
    print(f"      Exported to: {artifact_path}")

    print("[4/5] Generating derivatives…")
    derivative_ids = process_all_derivatives(artifact_id)
    for dtype, did in derivative_ids.items():
        print(f"      {dtype}: id={did}")

    print("[5/5] Exporting derivatives…")
    export_paths = export_all_derivatives(artifact_id)
    for path in export_paths:
        print(f"      {path}")

    _clear_active_session()
    print(f"\nDone. Artifact id={artifact_id} | {counts['processed']} screenshots processed.")
    print(f"Raw artifact:  {artifact_path}")


def cmd_regen_derivatives(args: argparse.Namespace) -> None:
    db.init_db()
    artifact_id = args.artifact_id
    print(f"Regenerating derivatives for artifact {artifact_id}…")
    derivative_ids = process_all_derivatives(artifact_id)
    export_paths = export_all_derivatives(artifact_id)
    for path in export_paths:
        print(f"  {path}")
    print("Done.")


def cmd_list_artifacts(args: argparse.Namespace) -> None:
    db.init_db()
    artifacts = db.list_raw_artifacts()
    if not artifacts:
        print("No artifacts found.")
        return
    for a in artifacts:
        print(f"  id={a['id']}  session={a['session_id']}  screenshots={a['source_screenshot_count']}  {a['created_at'][:16]}  {a['title']!r}")


def cmd_show_session(args: argparse.Namespace) -> None:
    db.init_db()
    session_id = _resolve_session(args.session)
    session = db.get_session(session_id)
    if not session:
        print(f"Session {session_id} not found")
        sys.exit(1)
    screenshots = db.get_session_screenshots(session_id)
    artifact = db.get_session_raw_artifact(session_id)

    print(f"\nSession {session_id}: {session['title']!r}")
    print(f"  Topic:    {session['topic'] or '—'}")
    print(f"  Category: {session['category'] or '—'}")
    print(f"  Started:  {session['start_time']}")
    print(f"  Ended:    {session['end_time'] or 'active'}")
    print(f"\nScreenshots: {len(screenshots)}")
    for s in screenshots:
        print(f"  id={s['id']} [{s['status']:9}] {s['filepath']}")
    if artifact:
        print(f"\nRaw Artifact: id={artifact['id']}  {artifact['title']!r}")
        derivatives = db.get_artifact_derivatives(artifact["id"])
        for d in derivatives:
            print(f"  {d['derivative_type']:20} [{d['status']}] id={d['id']}")
    else:
        print("\nNo artifact yet.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mnemo",
        description="L-Mnemo learning ingestion pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start-session
    p_start = sub.add_parser("start-session", help="Start a new study session")
    p_start.add_argument("--title", required=True, help="Session title (e.g. 'CIS101 Chapter 1')")
    p_start.add_argument("--topic", default="", help="Topic or subject area")
    p_start.add_argument("--category", default="", help="Category (e.g. 'CIS', 'Math')")

    # add-screenshot
    p_add = sub.add_parser("add-screenshot", help="Add screenshot(s) to the active session")
    p_add.add_argument("paths", nargs="+", help="Path(s) to screenshot file(s)")
    p_add.add_argument("--session", type=int, default=None, help="Session id (default: active)")

    # end-session
    p_end = sub.add_parser("end-session", help="End session and run the full pipeline")
    p_end.add_argument("--session", type=int, default=None, help="Session id (default: active)")
    p_end.add_argument("--title", default=None, help="Override artifact title")

    # regen-derivatives
    p_regen = sub.add_parser("regen-derivatives", help="Regenerate derivatives for an artifact")
    p_regen.add_argument("artifact_id", type=int, help="Raw artifact id")

    # list-artifacts
    sub.add_parser("list-artifacts", help="List all raw artifacts")

    # show-session
    p_show = sub.add_parser("show-session", help="Show session status")
    p_show.add_argument("--session", type=int, default=None, help="Session id (default: active)")

    args = parser.parse_args()
    commands = {
        "start-session": cmd_start_session,
        "add-screenshot": cmd_add_screenshot,
        "end-session": cmd_end_session,
        "regen-derivatives": cmd_regen_derivatives,
        "list-artifacts": cmd_list_artifacts,
        "show-session": cmd_show_session,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
