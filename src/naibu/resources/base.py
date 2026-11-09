"""Base classes for resource namespaces.

A resource groups the operations for one API collection (e.g. ``customers``)
and holds a reference back to its owning client for request dispatch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..async_client import AsyncNaibuClient
    from ..client import NaibuClient


class SyncResource:
    """Base class for synchronous resource namespaces."""

    def __init__(self, client: "NaibuClient") -> None:
        self._client = client


class AsyncResource:
    """Base class for asynchronous resource namespaces."""

    def __init__(self, client: "AsyncNaibuClient") -> None:
        self._client = client
