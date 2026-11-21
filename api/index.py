"""Vercel Python entry point for NoteVault.

Thin shim only — no app logic lives here. It re-exports the app's own
``NoteVaultHandler`` (notes_agent/web.py) under the name ``handler``,
which is what Vercel's Python runtime looks for when a function uses
``BaseHTTPRequestHandler``.

Two adaptations, both confined to this file:

1. Paths. The app's own server resolves the notes folder relative to
   the process working directory (config default "notes"). Vercel's
   working directory is not the project root, so the shared agent is
   built with an absolute notes_root resolved from THIS file's
   location: <project root>/notes.

2. Agent injection. ``NoteVaultHandler`` reads its agent from
   ``self.server.agent`` — under the app's own server, ``make_server``
   sets that attribute. On Vercel the runtime owns the server object,
   so this subclass attaches the shared agent to it before delegating
   to the original do_GET / do_POST. The agent is built once per
   warm container and reused across invocations.

Demo configuration: with no OTARI_AI_TOKEN set, the app runs in its
labelled mock mode, exactly as designed. The per-process ask budget
is raised from the CLI default of 5 to 200 so a public demo does not
die after five questions; the counter is in-memory only and resets
on every cold start regardless (see DEPLOY_NOTES.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from notes_agent.agent import NotesAgent  # noqa: E402
from notes_agent.config import config_from_env  # noqa: E402
from notes_agent.web import NoteVaultHandler  # noqa: E402

_AGENT: NotesAgent | None = None

# Public-demo budget: the CLI default (5 calls per process) would make
# the shared demo unusable; the counter is per-process and resets on
# cold start anyway, so this only stretches a warm container's demo.
DEMO_BUDGET_LIMIT = 200


def _get_agent() -> NotesAgent:
    global _AGENT
    if _AGENT is None:
        config = config_from_env(notes_root=PROJECT_ROOT / "notes")
        config.max_llm_calls_per_run = DEMO_BUDGET_LIMIT
        _AGENT = NotesAgent(config)
    return _AGENT


class handler(NoteVaultHandler):
    """NoteVaultHandler, plus lazy attachment of the shared agent."""

    def _attach_agent(self) -> None:
        if getattr(self.server, "agent", None) is None:
            self.server.agent = _get_agent()  # type: ignore[attr-defined]

    def setup(self) -> None:
        super().setup()
        self._attach_agent()

    def do_GET(self) -> None:  # noqa: N802
        self._attach_agent()
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        self._attach_agent()
        super().do_POST()
