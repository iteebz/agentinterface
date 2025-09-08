"""Universal component callbacks."""

import asyncio
import os
import uuid
from threading import Thread
from typing import Dict, Protocol, runtime_checkable

from .logger import logger


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
        self.callbacks: Dict[str, asyncio.Future] = {}
        self._started = False

    def start(self):
        """Start HTTP server if not already running."""
        if self._started:
            return

        try:
            import uvicorn
            from fastapi import FastAPI, Request
            from fastapi.middleware.cors import CORSMiddleware
        except ImportError:
            raise ImportError("pip install fastapi uvicorn for Http callbacks") from None

        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

        @app.post("/callback/{callback_id}")
        async def handle_callback(callback_id: str, request: Request):
            data = await request.json()
            if callback_id in self.callbacks and not self.callbacks[callback_id].done():
                self.callbacks[callback_id].set_result(
                    {"action": data.get("action"), "data": data.get("data")}
                )
            return {"status": "continued"}

        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="critical")

        Thread(target=run_server, daemon=True).start()
        self._started = True
        logger.debug(f"Started HTTP callback server on port {self.port}")


def _get_shared_server(port: int = 8228):
    """Get or create HTTP callback server."""
    if not hasattr(_get_shared_server, "instances"):
        _get_shared_server.instances = {}

    if port not in _get_shared_server.instances:
        server = _HttpCallbackServer(port)
        server.start()
        _get_shared_server.instances[port] = server

    return _get_shared_server.instances[port]


class Http(Callback):
    """HTTP-based component callback."""

    def __init__(self, id: str = None, port: int = 8228):
        """Create HTTP callback with self-managed lifecycle."""
        self.id = id or str(uuid.uuid4())
        self._future = asyncio.Future()
        self._server = _get_shared_server(port)
        self._server.callbacks[self.id] = self._future

    async def await_interaction(self, timeout: int = 300) -> dict:
        """Wait for user interaction with component."""
        try:
            return await asyncio.wait_for(self._future, timeout=timeout)
        finally:
            # Self-cleanup when done
            self._server.callbacks.pop(self.id, None)

    def endpoint(self) -> str:
        """Get endpoint string for component integration."""
        host = os.getenv("AI_CALLBACK_HOST", "localhost")
        return f"http://{host}:{self._server.port}/callback/{self.id}"
