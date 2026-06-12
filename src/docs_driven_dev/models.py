from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    level: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"level": self.level, "message": self.message, "path": self.path}
