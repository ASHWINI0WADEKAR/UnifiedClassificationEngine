# API Documentation

Base URL: `http://localhost:8000`

All classification responses use this schema:

```json
{
  "success": true,
  "modality": "text",
  "prediction": "general_text",
  "confidence": 0.65,
  "explanation": "Human-readable explanation",
  "model_used": "model-name",
  "processing_time": "0.001000s",
  "metadata": {}
}
```

## GET /health

Checks service readiness.

```powershell
curl http://localhost:8000/health
```

## GET /version

Returns version and supported modalities.

```powershell
curl http://localhost:8000/version
```

## POST /classify/text

Form field: `text`

```powershell
curl -X POST http://localhost:8000/classify/text -F "text=Hello world"
```

## POST /classify/image

Multipart file field: `file`

```powershell
curl -X POST http://localhost:8000/classify/image -F "file=@examples/sample.jpg"
```

## POST /classify/pdf

Multipart file field: `file`

```powershell
curl -X POST http://localhost:8000/classify/pdf -F "file=@examples/sample.pdf"
```

## POST /classify/audio

Multipart file field: `file`

```powershell
curl -X POST http://localhost:8000/classify/audio -F "file=@examples/sample.wav"
```
