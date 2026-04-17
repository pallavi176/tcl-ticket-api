"""API tests for ticket endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_ticket(client: AsyncClient) -> None:
    payload = {
        "title": "Bug: login fails",
        "description": "Steps to reproduce",
        "status": "open",
        "priority": "HIGH",
        "assigned_to": "alice",
    }
    r = await client.post("/tickets", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == "HIGH"
    tid = data["ticket_id"]

    g = await client.get(f"/tickets/{tid}")
    assert g.status_code == 200
    assert g.json()["ticket_id"] == tid


@pytest.mark.asyncio
async def test_get_not_found(client: AsyncClient) -> None:
    r = await client.get("/tickets/99999")
    assert r.status_code == 404
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "TICKET_NOT_FOUND"


@pytest.mark.asyncio
async def test_validation_error(client: AsyncClient) -> None:
    r = await client.post("/tickets", json={"title": "", "status": "x"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_ticket(client: AsyncClient) -> None:
    c = await client.post(
        "/tickets",
        json={
            "title": "T1",
            "description": None,
            "status": "open",
            "priority": "LOW",
            "assigned_to": None,
        },
    )
    tid = c.json()["ticket_id"]
    u = await client.put(f"/tickets/{tid}", json={"status": "closed"})
    assert u.status_code == 200
    assert u.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_empty_update_bad_request(client: AsyncClient) -> None:
    c = await client.post(
        "/tickets",
        json={
            "title": "T2",
            "description": None,
            "status": "open",
            "priority": "MEDIUM",
            "assigned_to": None,
        },
    )
    tid = c.json()["ticket_id"]
    u = await client.put(f"/tickets/{tid}", json={})
    assert u.status_code == 400
    assert u.json()["error"]["code"] == "EMPTY_UPDATE"


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["docs"] == "/docs"
    assert body["health"] == "/health"


@pytest.mark.asyncio
async def test_list_tickets(client: AsyncClient) -> None:
    await client.post(
        "/tickets",
        json={
            "title": "A",
            "description": None,
            "status": "open",
            "priority": "LOW",
            "assigned_to": None,
        },
    )
    r = await client.get("/tickets")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "ticket_id" in data[0]


@pytest.mark.asyncio
async def test_patch_single_field(client: AsyncClient) -> None:
    c = await client.post(
        "/tickets",
        json={
            "title": "Original",
            "description": "d",
            "status": "open",
            "priority": "MEDIUM",
            "assigned_to": None,
        },
    )
    tid = c.json()["ticket_id"]
    p = await client.patch(f"/tickets/{tid}", json={"title": "Renamed only"})
    assert p.status_code == 200
    assert p.json()["title"] == "Renamed only"
    assert p.json()["description"] == "d"


@pytest.mark.asyncio
async def test_close_ticket(client: AsyncClient) -> None:
    c = await client.post(
        "/tickets",
        json={
            "title": "To close",
            "description": None,
            "status": "open",
            "priority": "HIGH",
            "assigned_to": None,
        },
    )
    tid = c.json()["ticket_id"]
    cl = await client.post(f"/tickets/{tid}/close")
    assert cl.status_code == 200
    assert cl.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_ticket_lifecycle(client: AsyncClient) -> None:
    c = await client.post(
        "/tickets",
        json={
            "title": "Lifecycle",
            "description": "new",
            "status": "open",
            "priority": "LOW",
            "assigned_to": None,
        },
    )
    tid = c.json()["ticket_id"]

    lst = await client.get("/tickets")
    ids = {row["ticket_id"] for row in lst.json()}
    assert tid in ids

    await client.patch(f"/tickets/{tid}", json={"status": "in_progress"})
    g = await client.get(f"/tickets/{tid}")
    assert g.json()["status"] == "in_progress"

    await client.post(f"/tickets/{tid}/close")
    final = await client.get(f"/tickets/{tid}")
    assert final.json()["status"] == "closed"
