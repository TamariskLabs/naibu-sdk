"""Naibu SDK - the official Python client for the Naibu ERP system.

Quickstart:
    >>> from naibu import NaibuClient
    >>> client = NaibuClient(api_key="sk_live_...")
    >>> for customer in client.customers.list():
    ...     print(customer.name)

Async:
    >>> from naibu import AsyncNaibuClient
    >>> async with AsyncNaibuClient(api_key="sk_live_...") as client:
    ...     customer = await client.customers.retrieve("cus_123")
"""

from ._version import __version__
from .async_client import AsyncNaibuClient
from .auth import ApiKeyAuth, AuthProvider, OAuth2ClientCredentials
from .client import NaibuClient
from .exceptions import (
    NaibuAPIError,
    NaibuAuthenticationError,
    NaibuConfigError,
    NaibuConflictError,
    NaibuConnectionError,
    NaibuError,
    NaibuNotFoundError,
    NaibuPermissionError,
    NaibuRateLimitError,
    NaibuServerError,
    NaibuTimeoutError,
    NaibuValidationError,
)
from .models import Customer, Invoice, Order, OrderLine, Product

__all__ = [  # noqa: RUF022 - grouped by category for readability
    "__version__",
    # Clients
    "NaibuClient",
    "AsyncNaibuClient",
    # Auth
    "AuthProvider",
    "ApiKeyAuth",
    "OAuth2ClientCredentials",
    # Models
    "Customer",
    "Product",
    "Order",
    "OrderLine",
    "Invoice",
    # Exceptions
    "NaibuError",
    "NaibuConfigError",
    "NaibuAPIError",
    "NaibuAuthenticationError",
    "NaibuPermissionError",
    "NaibuNotFoundError",
    "NaibuConflictError",
    "NaibuValidationError",
    "NaibuRateLimitError",
    "NaibuServerError",
    "NaibuConnectionError",
    "NaibuTimeoutError",
]
