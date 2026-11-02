"""Socket-bound readiness signal for the local command and native runner."""

import asyncio
import json
import socket

import uvicorn


class ReadyServer(uvicorn.Server):
    async def startup(self, sockets: list[socket.socket] | None = None) -> None:
        await super().startup(sockets)
        if self.started:
            print(
                json.dumps({
                    "ready": True,
                    "url": f"http://127.0.0.1:{self.config.port}",
                }),
                flush=True,
            )

    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None:
        await asyncio.shield(super().shutdown(sockets))
