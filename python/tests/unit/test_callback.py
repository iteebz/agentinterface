"""Callback behavior tests."""

import asyncio

import pytest

from agentinterface.callback import Http


def test_http_instantiation():
    callback = Http()
    endpoint = callback.endpoint()
    assert endpoint.startswith("http://")


@pytest.mark.asyncio
async def test_http_registers_future():
    callback = Http()
    task = asyncio.create_task(callback.await_interaction(timeout=1))

    await asyncio.sleep(0)

    loop, future = callback._server.callbacks[callback.id]  # type: ignore[attr-defined]
    assert future.get_loop() is loop

    future.set_result({"action": "test", "data": {"ok": True}})

    result = await task
    assert result == {"action": "test", "data": {"ok": True}}
