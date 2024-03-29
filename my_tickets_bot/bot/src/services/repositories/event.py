"""Репозиторий для событий"""
import datetime

import asyncpg

from models import City, Location, User
from models.event import Event
from .queries import event as q
from ..event_time import localize_datetime


class EventRepo:
    """Репозиторий для события"""

    def __init__(
            self,
            connection: asyncpg.Connection,
    ):
        self._conn = connection

    async def save(
            self,
            user_id: int,
            name: str,
            event_time: datetime.datetime,
            location_id: int,
            link: str | None = None,
            event_id: int | None = None,
            end_time: datetime.datetime | None = None,
    ) -> Event:
        """Сохранения события"""
        if event_id is None:
            record = await self._conn.fetchrow(
                q.CREATE_EVENT,
                user_id, name, event_time, link, location_id, end_time,
            )
        else:
            record = await self._conn.fetchrow(
                q.UPDATE_EVENT,
                event_id, user_id, name, event_time, link, location_id, end_time,
            )
        return _convert_record_to_event(record)

    async def list(
            self,
            user_id: int | None = None,
            event_ids: list[int] | None = None,
            is_actual: bool | None = None,
            actual_time: datetime.datetime | None = None,
            limit: int = 5,
            offset: int = 0,
            asc: bool = True,
    ) -> list[Event]:
        """Получение списка событий"""
        records = await self._conn.fetch(q.GET_EVENTS, user_id, event_ids, is_actual, actual_time, limit, offset, asc)

        return [_convert_record_to_event(record) for record in records]

    async def get_count(
            self,
            user_id: int,
            is_actual: bool,
            actual_time: datetime.datetime,
    ):
        """Получение количества событий"""
        return await self._conn.fetchval(q.GET_COUNT, user_id, is_actual, actual_time)

    async def get(
            self,
            user_id: int | None,
            event_id: int,
    ) -> Event | None:
        """Получение события по идентификатору"""
        events = await self.list(user_id, [event_id])
        return events[0] if events else None

    async def get_id_by_uuid(
            self,
            event_uuid: str
    ) -> int | None:
        """Получение идентификатора события по UUID"""
        return await self._conn.fetchval(q.GET_ID_BY_UUID, event_uuid)

    async def delete(
            self,
            user_id: int,
            event_id: int,
    ):
        """Удаление события"""
        await self._conn.fetch(q.DELETE_EVENT, user_id, event_id)


def _convert_record_to_event(
        record: asyncpg.Record,
) -> Event:
    """Конвертация рекорда в событие"""

    event_time = record.get('event_time')
    end_time = record.get('event_end_time')

    if city_timezone := record.get('city_timezone'):
        event_time = localize_datetime(event_time, city_timezone) if event_time else None
        end_time = localize_datetime(end_time, city_timezone) if end_time else None

    return Event(
        event_id=record.get('event_id'),
        name=record.get('event_name'),
        time=event_time,
        end_time=end_time,
        link=record.get('event_link'),
        uuid=record.get('uuid'),
        user=User(
            user_id=record.get('user_id'),
        ),
        location=Location(
            location_id=record.get('location_id'),
            name=record.get('location_name'),
            address=record.get('location_address'),
            url=record.get('location_url'),
            city=City(
                city_id=record.get('city_id'),
                name=record.get('city_name'),
                timezone=record.get('city_timezone'),
            ),
        )
    )
