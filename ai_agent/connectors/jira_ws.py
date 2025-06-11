import json
from typing import Callable

from websocket import WebSocketApp


class JiraWebSocketClient:
    """Listen for Jira bug events over a WebSocket connection."""

    def __init__(self, ws_url: str):
        if not ws_url:
            raise ValueError("JIRA_WS_URL must be provided")
        self.ws_url = ws_url

    def listen(self, on_bug: Callable[[dict], None]) -> None:
        """Start listening and invoke *on_bug* for each received bug."""

        def _on_message(ws, message: str):
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                return
            issue = data.get("issue") or data
            if issue:
                on_bug(issue)

        ws = WebSocketApp(self.ws_url, on_message=_on_message)
        ws.run_forever()
