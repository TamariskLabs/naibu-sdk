"""Resource namespaces for the Naibu API."""

from .customers import AsyncCustomersResource, CustomersResource
from .invoices import AsyncInvoicesResource, InvoicesResource
from .orders import AsyncOrdersResource, OrdersResource
from .products import AsyncProductsResource, ProductsResource

__all__ = [
    "AsyncCustomersResource",
    "AsyncInvoicesResource",
    "AsyncOrdersResource",
    "AsyncProductsResource",
    "CustomersResource",
    "InvoicesResource",
    "OrdersResource",
    "ProductsResource",
]
