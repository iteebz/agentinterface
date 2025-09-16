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

        # Start cleanup task for abandoned callbacks
        try:
            if self._cleanup_task is None:
                self._cleanup_task = asyncio.create_task(self._cleanup_abandoned_callbacks())
        except RuntimeError:
            # No event loop running, skip cleanup task
            pass

        logger.debug(f"Started HTTP callback server on port {self.port}")

    async def _cleanup_abandoned_callbacks(self):
        """Clean up callbacks that have been waiting too long."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                current_time = asyncio.get_event_loop().time()
                abandoned = []

                for callback_id, future in self.callbacks.items():
                    if (
                        not future.done()
                        and hasattr(future, "_created_at")
                        and current_time - future._created_at > 600
                    ):
                        abandoned.append(callback_id)

                for callback_id in abandoned:
                    future = self.callbacks.pop(callback_id, None)
                    if future and not future.done():
                        future.cancel()
                        logger.debug(f"Cleaned up abandoned callback: {callback_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Callback cleanup error: {e}")


_servers: Dict[int, _HttpCallbackServer] = {}


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
        self._future = asyncio.Future()
        self._future._created_at = asyncio.get_event_loop().time()  # Track creation time
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
