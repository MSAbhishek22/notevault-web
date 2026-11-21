# NoteVault on Vercel — deploy notes

This folder is a deployment copy of NoteVault for Vercel's free tier.
The original repo (`../repo`) is untouched — it is under review in
other events. Everything in `run.py`, `notes_agent/` and `notes/` here
is a byte-identical copy of the original (verified with `diff -r`).

## What was added

- `api/index.py` — the Vercel Python entry point (the only new code).
- `vercel.json` — rewrites every path to `api/index.py`; no framework,
  no build command.
- `requirements.txt` — same as the original minus `pytest` (tests do
  not ship). `otari` stays; Vercel's Python 3.12 runtime installs it
  fine, and in mock mode the app never imports it.

## How the shim works

`notes_agent/web.py` already defines `NoteVaultHandler`, a
`BaseHTTPRequestHandler` subclass — exactly the shape Vercel's Python
runtime accepts as a `handler`. The shim subclasses it unchanged and
fixes the two things that differ between the app's own server and
Vercel:

1. **Notes path.** The app's server finds notes relative to the
   working directory. Vercel's working directory is not the project
   root, so the shim builds the agent with an absolute `notes_root`
   resolved from the shim file's location (`<project root>/notes`).
2. **Agent injection.** The handler reads its agent from
   `self.server.agent`; the app's `make_server` sets that, Vercel's
   runtime does not. The shim attaches one shared, lazily built agent
   to the server object in `setup()` / `do_GET` / `do_POST` before
   delegating to the original handler code.

## Changes to copied files

**None.** No file inside `notes_agent/`, `notes/` or `run.py` was
edited. All adaptation lives in `api/index.py`, including the one
configuration change below, which is done by setting a field on the
`Config` object in the shim — not by editing the package.

## Demo caveats (known, accepted for a public demo)

- **Budget is per-process and resets on cold start.** The app's ask
  budget is an in-memory counter. The shim raises the limit from the
  CLI default of 5 to 200 so the demo survives more than five
  questions per warm container, but a cold start resets the counter
  to zero, and a warm container's count is shared by all visitors.
  The budget meter in the UI is therefore a demo of the feature, not
  an accounting record. "Reset demo budget" in the UI resets it for
  everyone currently sharing that container.
- **Mock mode, labelled.** No `OTARI_AI_TOKEN` is set, so every
  answer comes from the app's deterministic offline stand-in and is
  prefixed `[mock]`, with a `[mock]` badge in the UI. Nothing about
  the demo claims a real Otari call happened. To run it for real
  later, set `OTARI_AI_TOKEN` in the Vercel project's environment
  variables — no code change needed.
- **Unauthenticated by design.** The app has no login. That is safe
  here only because the deployment bundles just the 4 sample notes
  from the repo — never point this deployment pattern at a private
  notes folder.
- **Serverless shape.** Each invocation is stateless apart from the
  shared warm-container agent above; concurrent visitors share one
  agent (and its budget counter), which the original threaded local
  server also did.
