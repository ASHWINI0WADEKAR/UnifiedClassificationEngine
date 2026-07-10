# Docker Verification

## Files Present

- `Dockerfile`: present.
- `docker-compose.yml`: present.

## Expected Command

```powershell
docker compose up --build
```

## Current Environment Result

Docker runtime could not be executed in this Codex environment because the Docker CLI is not installed or not available on PATH:

```text
docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## Developer Screenshot To Capture

After installing/opening Docker Desktop, run:

```powershell
docker compose up --build
```

Then in another terminal:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/version
```

Capture screenshots as:

- `screenshots/docker-compose.png`
- `screenshots/docker-health.png`
