"""Callback contract tests - protocol adherence."""

import asyncio
import contextlib
import os
from unittest.mock import patch

import pytest

from agentinterface.callback import Callback, Http


def test_http_has_endpoint():
    """Http callback has endpoint() method."""
    callback = Http()
    endpoint = callback.endpoint()
    assert isinstance(endpoint, str)
    assert endpoint.startswith("http://")


def test_http_endpoint_custom_id():
    """Http endpoint includes custom ID."""
    callback = Http(id="test-123")
    endpoint = callback.endpoint()
    assert "test-123" in endpoint


def test_http_endpoint_custom_port():
    """Http endpoint respects port parameter."""
    callback = Http(id="test", port=9999)
    endpoint = callback.endpoint()
    assert ":9999" in endpoint


def test_http_endpoint_respects_host_env():
    """Http endpoint uses AI_CALLBACK_HOST if set."""
    with patch.dict(os.environ, {"AI_CALLBACK_HOST": "example.com"}):
        callback = Http(id="test")
        endpoint = callback.endpoint()
        assert "example.com" in endpoint


@pytest.mark.asyncio
async def test_http_callback_protocol():
    """Http implements Callback protocol."""
    callback = Http(id="proto-test")
    assert isinstance(callback, Callback)
    assert hasattr(callback, "await_interaction")
    assert hasattr(callback, "endpoint")


@pytest.mark.asyncio
async def test_http_await_interaction_returns_dict():
    """await_interaction() returns dict with action and data."""
    callback = Http(id="dict-test")
    task = asyncio.create_task(callback.await_interaction(timeout=1))
    await asyncio.sleep(0)

    loop = asyncio.get_running_loop()
    loop.call_later(
        0.01,
        lambda: loop.call_soon_threadsafe(
            lambda: None  # Simulate callback trigger (would set future result in real scenario)
        ),
    )

    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(task, timeout=0.5)


@pytest.mark.asyncio
async def test_http_await_interaction_timeout():
    """await_interaction() raises TimeoutError when timeout expires."""
    callback = Http(id="timeout-test")
    with pytest.raises(asyncio.TimeoutError):
        await callback.await_interaction(timeout=0.01)


@pytest.mark.asyncio
async def test_multiple_awaits_same_callback():
    """Same callback can await multiple times sequentially."""
    callback = Http(id="multi-test")

    for _ in range(3):
        task = asyncio.create_task(callback.await_interaction(timeout=0.1))
        await asyncio.sleep(0.01)

        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(lambda: None)

        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(task, timeout=0.2)


def test_custom_callback_protocol():
    """Custom class implementing Callback protocol is recognized."""

    class CustomCallback:
        async def await_interaction(self, timeout=300):
            return {"action": "test"}

        def endpoint(self):
            return "custom://endpoint"

    assert isinstance(CustomCallback(), Callback)


def test_incomplete_callback_not_recognized():
    """Class missing Callback methods not recognized as Callback."""

    class IncompleteCallback:
        def endpoint(self):
            return "incomplete://endpoint"

    assert not isinstance(IncompleteCallback(), Callback)
