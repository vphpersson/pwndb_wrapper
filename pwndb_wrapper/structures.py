from dataclasses import dataclass, field


@dataclass(frozen=True)
class PwndbEntry:
    id: int = field(hash=True)
    luser: str
    domain: str
    password: str
