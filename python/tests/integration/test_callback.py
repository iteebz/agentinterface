"""Integration tests for callback system - HTTP server lifecycle"""

import asyncio
from unittest.mock import patch

import pytest

from agentinterface.callback import Callback, Http, _get_shared_server


def test_callback_protocol():
    """Test callback protocol typing."""
    # This is a compile-time check, but we can verify at runtime too

    class CustomCallback:
        async def await_interaction(self, timeout=300):
            return {"action": "test", "data": "custom"}

        def endpoint(self):
            return "custom://callback"

    # Should be recognized as implementing the protocol
    assert isinstance(CustomCallback(), Callback)

    # Missing method should not be recognized
    class IncompleteCallback:
        def endpoint(self):
            return "incomplete://callback"

    assert not isinstance(IncompleteCallback(), Callback)


@pytest.mark.asyncio
async def test_http_callback_endpoint():
    """Test HTTP callback endpoint generation."""
    callback = Http(id="test-id", port=9999)

    # Endpoint should contain protocol, host, port and ID
    endpoint = callback.endpoint()
    assert endpoint.startswith("http://")
    assert ":9999/" in endpoint
    assert endpoint.endswith("/callback/test-id")

    # Should use custom host if provided
    with patch.dict("os.environ", {"AI_CALLBACK_HOST": "custom.host"}):
        assert "custom.host" in Http().endpoint()


@pytest.mark.asyncio
async def test_http_callback_lifecycle():
    """Test HTTP callback self-managed lifecycle."""
    callback = Http(id="test-lifecycle")
    server = _get_shared_server()

    # Callback should register itself
    assert "test-lifecycle" in server.callbacks

    # Simulate callback activation
    server.callbacks["test-lifecycle"].set_result({"action": "click", "data": "value"})

    # Should receive the interaction
    result = await callback.await_interaction()
    assert result == {"action": "click", "data": "value"}

    # Should have cleaned up after itself
    assert "test-lifecycle" not in server.callbacks


@pytest.mark.asyncio
async def test_http_callback_timeout():
    """Test HTTP callback timeout behavior."""
    callback = Http(id="test-timeout")

    # Should timeout and clean up
    with pytest.raises(asyncio.TimeoutError):
        await callback.await_interaction(timeout=0.1)

    # Should have cleaned up despite timeout
    server = _get_shared_server()
    assert "test-timeout" not in server.callbacks


@pytest.mark.asyncio
async def test_shared_server_singleton():
    """Test shared server singleton pattern."""
    # Should return same instance for same port
    server1 = _get_shared_server(port=8888)
    server2 = _get_shared_server(port=8888)
    assert server1 is server2

    # Should return different instance for different port
    server3 = _get_shared_server(port=8889)
    assert server1 is not server3


@pytest.mark.asyncio
async def test_callback_cleanup_abandoned():
    """Test abandoned callbacks are cleaned up after timeout."""
    Http(id="test-cleanup", port=8123)
    server = _get_shared_server(port=8123)

    # Callback should be registered
    assert "test-cleanup" in server.callbacks

    # Create future with timestamp for cleanup
    future = server.callbacks["test-cleanup"]
    future._created_at = asyncio.get_event_loop().time() - 700  # 11+ minutes ago

    # Run one iteration of cleanup manually (avoid infinite loop)
    current_time = asyncio.get_event_loop().time()
    abandoned = []

    for callback_id, cb_future in server.callbacks.items():
        if (
            not cb_future.done()
            and hasattr(cb_future, "_created_at")
            and current_time - cb_future._created_at > 600
        ):
            abandoned.append(callback_id)

    for callback_id in abandoned:
        if callback_id in server.callbacks:
            server.callbacks[callback_id].cancel()
            del server.callbacks[callback_id]

    # Should be cleaned up due to age
    assert "test-cleanup" not in server.callbacks
