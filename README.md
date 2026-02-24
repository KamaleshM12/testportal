# Secure Code Execution Engine (FastAPI)

This project provides a FastAPI-based secure code execution engine that runs user code inside Docker containers with resource limits and network disabled.

Structure:
- `runner/Dockerfile` - minimal image with compilers and interpreters
- `app/` - FastAPI app, executor, and docker runner
- `requirements.txt` - Python deps

Run FastAPI server:

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Build runner image (on host with Docker):

```powershell
docker build -t testportal/runner:latest ./runner
```

Publish runner image via GitHub Actions
--------------------------------------

This repo includes a GitHub Actions workflow that builds and publishes the runner image to GitHub Container Registry (GHCR) on push to `main`.

To pull the published image locally (after the workflow runs),

```powershell
docker pull ghcr.io/<OWNER>/testportal-runner:latest
```

Notes & hardening
- The runner containers are started with `network_mode='none'`, `read_only` filesystem, dropped capabilities, and resource limits.
- You should enable `packages: write` permission for the workflow (the provided workflow sets permissions accordingly).
- The included `runner/seccomp.json` is a conservative example; for production, tune and test this profile.

