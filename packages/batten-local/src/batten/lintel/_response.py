"""Bound one HTTP response until the ingress-owned Host scope closes."""

from starlette.types import Message, Send


class BufferedResponse:
    def __init__(self, maximum: int):
        self.maximum = maximum
        self.start: Message | None = None
        self.body = bytearray()
        self.complete = False
        self.used = 0

    async def capture(self, message: Message) -> None:
        kind = message.get("type")
        if kind == "http.response.start":
            if self.start is not None or type(message.get("status")) is not int:
                raise ValueError("invalid response start")
            headers = [
                (bytes(key), bytes(value)) for key, value in message.get("headers", [])
            ]
            self.used += sum(len(key) + len(value) for key, value in headers)
            self.start = {"type": kind, "status": message["status"], "headers": headers}
        elif kind == "http.response.body":
            if self.start is None or self.complete:
                raise ValueError("invalid response body")
            chunk = message.get("body", b"")
            if (
                type(chunk) is not bytes
                or type(message.get("more_body", False)) is not bool
            ):
                raise ValueError("invalid response chunk")
            self.used += len(chunk)
            if self.used <= self.maximum:
                self.body.extend(chunk)
            self.complete = not message.get("more_body", False)
        else:
            raise ValueError("unsupported response event")
        if self.used > self.maximum:
            raise ValueError("response capacity exceeded")

    async def flush(self, send: Send) -> None:
        if self.start is None or not self.complete:
            raise ValueError("response did not complete")
        await send(self.start)
        await send({"type": "http.response.body", "body": bytes(self.body)})
