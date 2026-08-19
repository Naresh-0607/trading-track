from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserEntity:
    id: UUID
    name: str
    email: str
    created_at: datetime

