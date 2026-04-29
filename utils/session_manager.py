import json
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from utils.path_tool import get_abs_path

DATA_DIR = get_abs_path("data/sessions")
os.makedirs(DATA_DIR, exist_ok=True)
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions_index.json")


class StorageInterface(ABC):
    @abstractmethod
    def save_session(self, session: dict) -> None:
        ...

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        ...

    @abstractmethod
    def load_session(self, session_id: str) -> Optional[dict]:
        ...

    @abstractmethod
    def list_sessions(self) -> list[dict]:
        ...

    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        ...


class LocalJSONStorage(StorageInterface):
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.index_file = os.path.join(self.data_dir, "sessions_index.json")
        self._ensure_index()

    def _ensure_index(self):
        if not os.path.exists(self.index_file):
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)

    def _session_file_path(self, session_id: str) -> str:
        return os.path.join(self.data_dir, f"{session_id}.json")

    def _read_index(self) -> list[dict]:
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_index(self, index: list[dict]):
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save_session(self, session: dict) -> None:
        session_id = session["id"]
        with open(self._session_file_path(session_id), "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)

        index = self._read_index()
        index_entry = {
            "id": session["id"],
            "name": session.get("name", "新会话"),
            "created_at": session.get("created_at", datetime.now().isoformat()),
            "updated_at": session.get("updated_at", datetime.now().isoformat()),
            "message_count": len(session.get("messages", []))
        }
        existing = [i for i in index if i["id"] == session_id]
        if existing:
            for i, entry in enumerate(index):
                if entry["id"] == session_id:
                    index[i] = index_entry
                    break
        else:
            index.append(index_entry)
        self._write_index(index)

    def delete_session(self, session_id: str) -> None:
        session_file = self._session_file_path(session_id)
        if os.path.exists(session_file):
            os.remove(session_file)
        index = self._read_index()
        index = [i for i in index if i["id"] != session_id]
        self._write_index(index)

    def load_session(self, session_id: str) -> Optional[dict]:
        session_file = self._session_file_path(session_id)
        if not os.path.exists(session_file):
            return None
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_sessions(self) -> list[dict]:
        return self._read_index()

    def session_exists(self, session_id: str) -> bool:
        return os.path.exists(self._session_file_path(session_id))


class SessionManager:
    def __init__(self, storage: Optional[StorageInterface] = None):
        self.storage = storage or LocalJSONStorage()

    def create_session(self, name: Optional[str] = None, force: bool = False) -> dict:
        if not force:
            empty_session = self._find_empty_session()
            if empty_session:
                return empty_session

        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        session = {
            "id": session_id,
            "name": name or f"会话 {datetime.now().strftime('%m-%d %H:%M')}",
            "created_at": now,
            "updated_at": now,
            "messages": []
        }
        self.storage.save_session(session)
        return session

    def _find_empty_session(self) -> Optional[dict]:
        sessions = self.storage.list_sessions()
        for s in sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True):
            full = self.storage.load_session(s["id"])
            if full and len(full.get("messages", [])) == 0:
                return full
        return None

    def get_session(self, session_id: str) -> Optional[dict]:
        return self.storage.load_session(session_id)

    def save_message(self, session_id: str, role: str, content: str) -> dict:
        session = self.storage.load_session(session_id)
        if session is None:
            return None

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        session["messages"].append(message)
        session["updated_at"] = datetime.now().isoformat()
        if not session["messages"]:
            session["name"] = content[:20] + ("..." if len(content) > 20 else "")
        self.storage.save_session(session)
        return session

    def delete_session(self, session_id: str) -> None:
        self.storage.delete_session(session_id)

    def list_sessions(self) -> list[dict]:
        sessions = self.storage.list_sessions()
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_message_count(self, session_id: str) -> int:
        session = self.storage.load_session(session_id)
        if session is None:
            return 0
        return len(session.get("messages", []))

    def has_empty_session(self) -> bool:
        return self._find_empty_session() is not None

    def rename_session(self, session_id: str, name: str) -> None:
        session = self.storage.load_session(session_id)
        if session is None:
            return
        session["name"] = name
        session["updated_at"] = datetime.now().isoformat()
        self.storage.save_session(session)
