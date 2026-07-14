"""Deterministic replay artifact writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from contracts import ReplayArtifact
from provenance.hashing import stable_json_hash


class ReplayArtifactWriter:
    """Persist canonical classification responses for deterministic replay."""

    def __init__(self, artifact_dir: str | Path = "replay/artifacts") -> None:
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def write(self, payload: Dict[str, Any], request_id: str) -> ReplayArtifact:
        serializable = dict(payload)
        serializable["replay"] = None
        artifact_hash = stable_json_hash(serializable)
        artifact_id = f"{request_id}-{artifact_hash[:12]}"
        path = self.artifact_dir / f"{artifact_id}.json"
        path.write_text(json.dumps(serializable, indent=2, sort_keys=True, default=str), encoding="utf-8")
        file_hash = stable_json_hash(json.loads(path.read_text(encoding="utf-8")))
        return ReplayArtifact(artifact_id=artifact_id, path=str(path), sha256=file_hash)
