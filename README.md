# NoteVault (web deployment)

NoteVault is a local-first notes agent. It searches your notes on your own machine first, answers only from what it finds, shows the notes it used, and says so when nothing matches instead of guessing.

This repo is the Vercel deployment of the full project: https://github.com/MSAbhishek22/notevault — the app code here is the same code, with a thin Vercel entry point in api/index.py (see DEPLOY_NOTES.md).

The public demo runs in mock mode: no Otari token is set, so answers come from a built-in offline stand-in and are prefixed [mock]. It serves only the 4 sample notes in notes/.

Built by M S Abhishek.
