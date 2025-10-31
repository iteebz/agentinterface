"""Universal component callbacks."""

import asyncio
import logging
import os
import uuid
from threading import Thread
from typing import Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

ABANDONED_CALLBACK_TIMEOUT = 600


@runtime_checkable
class Callback(Protocol):
    """Universal component event callbacks."""

    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction with component."""
        ...

    def endpoint(self) -> str:
        """Get endpoint string for component integration."""
        ...


class _HttpCallbackServer:
    """Internal HTTP server for callbacks."""

    def __init__(self, port: int = 8228):
        self.port = port
        self.callbacks: dict[str, tuple[asyncio.AbstractEventLoop, asyncio.Future]] = {}
        self._started = False
        self._cleanup_task = None

    def start(self):
        """Start HTTP server if not already running."""
        if self._started:
            return

        try:
            import uvicorn
            from fastapi import FastAPI, Request
            from fastapi.middleware.cors import CORSMiddleware
        except ImportError:
            raise ImportError("pip install fastapi uvicorn") from None

        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

        @app.post("/callback/{callback_id}")
        async def handle_callback(callback_id: str, request: Request):
            data = await request.json()
            if callback_id in self.callbacks:
                loop, future = self.callbacks[callback_id]
                if not future.done():
                    loop.call_soon_threadsafe(
                        future.set_result,
                        {"action": data.get("action"), "data": data.get("data")},
                    )
            return {"status": "continued"}

        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="critical")

        Thread(target=run_server, daemon=True).start()
        self._started = True

        try:
            loop = asyncio.get_running_loop()
            if self._cleanup_task is None:
                self._cleanup_task = loop.create_task(self._cleanup_abandoned_callbacks())
        except RuntimeError:
            pass

    async def _cleanup_abandoned_callbacks(self):
        """Clean up callbacks that have been waiting too long."""
        while True:
            try:
                await asyncio.sleep(60)
                current_time = asyncio.get_event_loop().time()
                abandoned = []

                for callback_id, (_loop, future) in list(self.callbacks.items()):
                    if (
                        not future.done()
                        and hasattr(future, "_created_at")
                        and current_time - future._created_at > ABANDONED_CALLBACK_TIMEOUT
                    ):
                        abandoned.append(callback_id)

                for callback_id in abandoned:
                    entry = self.callbacks.pop(callback_id, None)
                    if entry:
                        _loop, future = entry
                        if not future.done():
                            _loop.call_soon_threadsafe(future.cancel)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Callback cleanup error: {e}")


_servers: dict[int, _HttpCallbackServer] = {}


def _get_shared_server(port: int = 8228):
    """Get or create HTTP callback server."""
    if port not in _servers:
        server = _HttpCallbackServer(port)
        server.start()
        _servers[port] = server
    return _servers[port]


class Http(Callback):
    """HTTP-based component callback."""

    def __init__(self, id: str = None, port: int = 8228):
        """Create HTTP callback with self-managed lifecycle."""
        self.id = id or str(uuid.uuid4())
        self._server = _get_shared_server(port)
        self._future: Optional[asyncio.Future] = None

    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction with component."""
        try:
            if self._future is None or self._future.done():
                loop = asyncio.get_running_loop()
                future = loop.create_future()
                future._created_at = loop.time()
                self._future = future
                self._server.callbacks[self.id] = (loop, future)

            return await asyncio.wait_for(self._future, timeout=timeout)
        finally:
            self._server.callbacks.pop(self.id, None)
            if self._future and self._future.done():
                self._future = None

    def endpoint(self) -> str:
        """Get endpoint string for component integration."""
        host = os.getenv("AI_CALLBACK_HOST", "localhost")
        return f"http://{host}:{self._server.port}/callback/{self.id}"
