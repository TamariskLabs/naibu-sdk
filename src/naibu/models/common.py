"""Example resource models for the Naibu ERP domain.

These illustrate the modeling conventions used across the SDK. Extend or
replace them as the real API surface is implemented.
"""

from __future__ import annotations

import dataclasses
from typing import Optional

from .base import BaseModel


@dataclasses.dataclass
class Customer(BaseModel):
    """A customer record in the ERP."""

    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclasses.dataclass
class Product(BaseModel):
    """A product or SKU in the catalog."""

    id: Optional[str] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    quantity_on_hand: Optional[int] = None


@dataclasses.dataclass
class OrderLine(BaseModel):
    """A single line item on an order."""

    product_id: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


@dataclasses.dataclass
class Order(BaseModel):
    """A sales order."""

    id: Optional[str] = None
    customer_id: Optional[str] = None
    status: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    lines: Optional[list[OrderLine]] = None
    created_at: Optional[str] = None


@dataclasses.dataclass
class Invoice(BaseModel):
    """An invoice generated from an order."""

    id: Optional[str] = None
    order_id: Optional[str] = None
    customer_id: Optional[str] = None
    status: Optional[str] = None
    amount_due: Optional[float] = None
    currency: Optional[str] = None
    due_date: Optional[str] = None
