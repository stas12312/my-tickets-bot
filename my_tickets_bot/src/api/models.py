import datetime

from pydantic import BaseModel


class Parser(BaseModel):
    """Модель парсера для API"""
    name: str
    events_count: int | None
    timestamp: datetime.datetime | None
    timezone: str
    url: str