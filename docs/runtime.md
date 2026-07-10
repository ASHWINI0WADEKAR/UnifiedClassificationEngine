# Runtime Verification

## Generate Samples

```powershell
python scripts\generate_samples.py
```

Expected files:

- `examples/sample.txt`
- `examples/sample.jpg`
- `examples/sample.pdf`
- `examples/sample.wav`

## CLI Runtime

```powershell
python demo.py
```

Expected result: all four classifiers print `Prediction`, `Confidence`, `Explanation`, `Model Used`, and `Processing Time`, followed by `Demo completed successfully.`

## API Runtime

Terminal 1:

```powershell
python app.py
```

Terminal 2:

```powershell
python scripts\verify_api.py
```

Expected result: `/health`, `/version`, `/classify/text`, `/classify/image`, `/classify/pdf`, and `/classify/audio` pass.

## Docker Runtime

```powershell
docker compose up --build
```

Then verify:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/version
```

## Screenshot Instructions

Save proof screenshots under `screenshots/`:

- `screenshots/cli-demo.png`: terminal after `python demo.py` completes.
- `screenshots/unit-tests.png`: terminal after unit tests pass.
- `screenshots/api-verification.png`: terminal after `python scripts\verify_api.py` passes.
- `screenshots/docker-health.png`: Docker compose running and `/health` response.
- `screenshots/fastapi-docs.png`: browser opened to `http://localhost:8000/docs`.
