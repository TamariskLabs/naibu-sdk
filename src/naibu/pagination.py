"""Cursor/offset pagination helpers.

The Naibu API returns list responses shaped like::

    {"data": [...], "next_cursor": "abc", "has_more": true}

:class:`SyncPage` and :class:`AsyncPage` lazily walk every page so callers can
simply iterate over all items without managing cursors themselves.
"""

from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    TypeVar,
)

T = TypeVar("T")

# A fetcher takes an optional cursor and returns a raw page payload.
SyncFetcher = Callable[[Optional[str]], Mapping[str, Any]]
AsyncFetcher = Callable[[Optional[str]], Awaitable[Mapping[str, Any]]]


def _extract(
    payload: Mapping[str, Any], parse: Callable[[Any], T]
) -> tuple[List[T], Optional[str]]:
    items_raw = payload.get("data", payload.get("items", []))
    items = [parse(item) for item in items_raw]
    cursor = payload.get("next_cursor") or payload.get("next")
    has_more = payload.get("has_more", bool(cursor))
    return items, (cursor if has_more else None)


class SyncPage(Generic[T]):
    """Iterable over every item across all pages (synchronous)."""

    def __init__(self, fetcher: SyncFetcher, parse: Callable[[Any], T]) -> None:
        self._fetcher = fetcher
        self._parse = parse

    def __iter__(self) -> Iterator[T]:
        cursor: Optional[str] = None
        while True:
            payload = self._fetcher(cursor)
            items, cursor = _extract(payload, self._parse)
            yield from items
            if cursor is None:
                return

    def first_page(self) -> List[T]:
        """Return only the first page of results."""
        items, _ = _extract(self._fetcher(None), self._parse)
        return items


class AsyncPage(Generic[T]):
    """Async-iterable over every item across all pages."""

    def __init__(self, fetcher: AsyncFetcher, parse: Callable[[Any], T]) -> None:
        self._fetcher = fetcher
        self._parse = parse

    async def __aiter__(self) -> AsyncIterator[T]:
        cursor: Optional[str] = None
        while True:
            payload = await self._fetcher(cursor)
            items, cursor = _extract(payload, self._parse)
            for item in items:
                yield item
            if cursor is None:
                return

    async def first_page(self) -> List[T]:
        """Return only the first page of results."""
        items, _ = _extract(await self._fetcher(None), self._parse)
        return items
