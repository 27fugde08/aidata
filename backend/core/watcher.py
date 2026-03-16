import os
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi import WebSocket

from .event_engine import events

class LiveSyncHandler(FileSystemEventHandler):
    """
    Xử lý sự kiện file thay đổi và gửi qua WebSocket + EventEngine.
    """
    def __init__(self, websocket: WebSocket, loop):
        self.websocket = websocket
        self.loop = loop

    def on_modified(self, event):
        self._send_event("modified", event.src_path)

    def on_created(self, event):
        self._send_event("created", event.src_path)

    def on_deleted(self, event):
        self._send_event("deleted", event.src_path)

    def _send_event(self, type: str, path: str):
        if "__pycache__" in path or ".git" in path or ".memory" in path:
            return
            
        # Gửi tới UI qua WebSocket
        asyncio.run_coroutine_threadsafe(
            self.websocket.send_json({"type": "file_change", "event": type, "path": path}),
            self.loop
        )
        
        # Phát sự kiện vào hệ thống để trigger automation
        asyncio.run_coroutine_threadsafe(
            events.emit("FILE_CHANGE", {"event": type, "path": path}),
            self.loop
        )

class Watcher:
    """
    Quản lý tiến trình theo dõi file.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.observer = Observer()

    def start(self, websocket: WebSocket, loop):
        event_handler = LiveSyncHandler(websocket, loop)
        self.observer.schedule(event_handler, self.root_dir, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
