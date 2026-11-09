"""Base model utilities.

Models are lightweight dataclasses with ``from_dict`` / ``to_dict`` helpers so
the SDK stays dependency-free (no pydantic requirement) while remaining fully
typed. Unknown fields returned by the API are preserved on ``extra`` so forward
compatibility never raises.
"""

from __future__ import annotations

import dataclasses
from typing import Any, ClassVar, Mapping, TypeVar

T = TypeVar("T", bound="BaseModel")


@dataclasses.dataclass
class BaseModel:
    """Base class for all API resource models."""

    #: Fields present on the wire but not declared on the model.
    extra: dict[str, Any] = dataclasses.field(default_factory=dict, repr=False)

    #: Declared field names, computed lazily per-subclass.
    _field_names: ClassVar[frozenset[str]] = frozenset()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

    @classmethod
    def _known_fields(cls) -> frozenset[str]:
        return frozenset(f.name for f in dataclasses.fields(cls) if f.name != "extra")

    @classmethod
    def from_dict(cls: type[T], data: Mapping[str, Any]) -> T:
        """Construct an instance from an API payload, capturing unknown keys."""
        known = cls._known_fields()
        kwargs: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        for key, value in data.items():
            if key in known:
                kwargs[key] = value
            else:
                extra[key] = value
        instance = cls(**kwargs)
        instance.extra = extra
        return instance

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-ready dict, dropping ``None`` and merging extras."""
        result: dict[str, Any] = {}
        for f in dataclasses.fields(self):
            if f.name == "extra":
                continue
            value = getattr(self, f.name)
            if value is None:
                continue
            result[f.name] = _serialize(value)
        result.update(self.extra)
        return result


def _serialize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.to_dict()
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    return value
