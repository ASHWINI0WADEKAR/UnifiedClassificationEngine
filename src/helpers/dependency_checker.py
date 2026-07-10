"""Dependency availability checks for optional AI packages."""

from __future__ import annotations

import importlib.util
import shutil
from typing import Dict


class DependencyChecker:
    """Check whether optional runtime dependencies are available."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, bool | str]] = {}

    def check(self, package_name: str) -> Dict[str, bool | str]:
        """Check whether a dependency is available.

        Args:
            package_name: Package or executable name to test.

        Returns:
            A status mapping describing the dependency availability.
        """
        if package_name in self._cache:
            return self._cache[package_name]

        module_spec = importlib.util.find_spec(package_name)
        executable = shutil.which(package_name)
        available = bool(module_spec or executable)
        status = {
            "available": available,
            "package": package_name,
            "module": bool(module_spec),
            "executable": bool(executable),
        }
        self._cache[package_name] = status
        return status
