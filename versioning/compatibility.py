"""Semantic compatibility checks for classification contracts."""

from __future__ import annotations

from dataclasses import dataclass

from versioning import CONTRACT_VERSION, SUPPORTED_CONTRACT_VERSIONS


@dataclass(frozen=True)
class CompatibilityResult:
    """Result for a contract compatibility check."""

    compatible: bool
    requested_version: str
    current_version: str
    reason: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "compatible": self.compatible,
            "requested_version": self.requested_version,
            "current_version": self.current_version,
            "reason": self.reason,
        }


class ContractCompatibilityChecker:
    """Check whether a caller contract version is supported."""

    def __init__(self, current_version: str = CONTRACT_VERSION) -> None:
        self.current_version = current_version

    def check(self, requested_version: str) -> CompatibilityResult:
        if requested_version in SUPPORTED_CONTRACT_VERSIONS:
            return CompatibilityResult(True, requested_version, self.current_version, "Contract version is supported.")
        return CompatibilityResult(False, requested_version, self.current_version, "Unsupported contract version.")

    def require_compatible(self, requested_version: str) -> None:
        result = self.check(requested_version)
        if not result.compatible:
            raise ValueError(result.reason)
