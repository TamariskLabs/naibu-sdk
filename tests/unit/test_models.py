"""Tests for the model layer."""

from __future__ import annotations

from naibu.models.common import Customer, Order, OrderLine


def test_from_dict_captures_extra() -> None:
    customer = Customer.from_dict({"id": "c1", "name": "Acme", "unknown": 42})
    assert customer.id == "c1"
    assert customer.name == "Acme"
    assert customer.extra == {"unknown": 42}


def test_to_dict_drops_none_and_merges_extra() -> None:
    customer = Customer(id="c1", name="Acme")
    customer.extra = {"region": "EU"}
    assert customer.to_dict() == {"id": "c1", "name": "Acme", "region": "EU"}


def test_nested_serialization() -> None:
    order = Order(id="o1", lines=[OrderLine(product_id="p1", quantity=2)])
    assert order.to_dict() == {
        "id": "o1",
        "lines": [{"product_id": "p1", "quantity": 2}],
    }


def test_roundtrip() -> None:
    data = {"id": "c1", "name": "Acme", "email": "a@b.com"}
    customer = Customer.from_dict(data)
    assert customer.to_dict() == data
