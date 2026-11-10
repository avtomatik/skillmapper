import json
import os
import tempfile
from pathlib import Path
from threading import RLock


class JsonTokenStore:
    """Atomic local JSON token persistence; restrict permissions where supported."""

    def __init__(self, path: Path | str):
        self._path = Path(path)
        self._lock = RLock()

    def load_tokens(self) -> dict | None:
        with self._lock:
            if not self._path.exists():
                return None
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(
                    f"Cannot read token store {self._path}"
                ) from exc
            if not isinstance(data, dict):
                raise RuntimeError("Token store must contain a JSON object.")
            return data

    def save_tokens(self, tokens: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(
            prefix=f".{self._path.name}.", dir=self._path.parent
        )
        try:
            try:
                os.fchmod(fd, 0o600)
            except OSError:
                pass
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(tokens, stream, indent=2, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self._path)
            try:
                self._path.chmod(0o600)
            except OSError:
                pass
        except Exception:
            try:
                os.unlink(name)
            except OSError:
                pass
            raise
