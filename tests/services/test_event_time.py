"""Тесты работы со временем события"""
import datetime
from unittest.mock import patch

import pytest
import pytz

from services.event_time import get_beatify_datetime, get_left_time, parse_datetime, get_localtime

testdata = [
    (6, 2, 23, 14, 10, '6 Февраля в 14:10 (Пн)'),
    (7, 8, 22, 9, 2, '7 Августа в 9:02 (Вс)'),
]


@pytest.mark.parametrize('day,month,year,hour,minute,result', testdata)
def test_beautify_datetime(day: int, month: int, year: int, hour: int, minute: int, result):
    """Проверка преобразования даты в красивый вид"""
    datetime_ = datetime.datetime(year, month, day, hour, minute)

    beautify_time = get_beatify_datetime(datetime_)
    assert beautify_time == result


testdata = [
    (datetime.datetime(2022, 2, 1, 14, 30), datetime.datetime(2023, 4, 3, 15, 30), '1 год 2 месяца'),
    (datetime.datetime(2022, 4, 3, 15, 30), datetime.datetime(2023, 4, 3, 15, 30), '1 год'),
    (datetime.datetime(2023, 1, 1, 14, 30), datetime.datetime(2023, 4, 3, 15, 30), '3 месяца 2 дня'),
    (datetime.datetime(2023, 1, 3, 14, 30), datetime.datetime(2023, 4, 3, 15, 30), '3 месяца'),
    (datetime.datetime(2023, 4, 2, 10, 15), datetime.datetime(2023, 4, 3, 15, 30), '1 день 5 часов'),
    (datetime.datetime(2023, 4, 2, 15, 15), datetime.datetime(2023, 4, 3, 15, 30), '1 день'),
    (datetime.datetime(2023, 4, 3, 14, 00), datetime.datetime(2023, 4, 3, 15, 30), '1 час 30 минут'),
    (datetime.datetime(2023, 4, 3, 14, 30), datetime.datetime(2023, 4, 3, 15, 30), '1 час'),
    (datetime.datetime(2023, 4, 3, 15, 19), datetime.datetime(2023, 4, 3, 15, 30), '11 минут'),
    (datetime.datetime(2023, 4, 5, 15, 15), datetime.datetime(2023, 4, 3, 15, 30), None),
]


@pytest.mark.parametrize('first,second,result', testdata)
def test_get_interval(first: datetime.datetime, second: datetime.datetime, result: str):
    """Проверка получения оставшегося времени"""
    assert get_left_time(first, second) == result


testdata = [
    ('01.02.23 20:30', datetime.datetime(2023, 2, 1, 20, 30)),
    ('01.02.23 20 30', datetime.datetime(2023, 2, 1, 20, 30)),
    ('10.06 20:30', datetime.datetime(2023, 6, 10, 20, 30)),
    ('09.06 20:30', datetime.datetime(2024, 6, 9, 20, 30)),
    ('20 МаРта 21:30', datetime.datetime(2024, 3, 20, 21, 30)),
    ('28 Октября 19:30', datetime.datetime(2023, 10, 28, 19, 30)),
    ('31 февраля 21:30', None),
]


@pytest.mark.parametrize('input_time,result', testdata)
def test_parse_datetime(input_time: str, result: datetime.datetime | None):
    """Проверка парсинга введенного времени"""
    now = datetime.datetime(2023, 6, 10)
    parsed_datetime = parse_datetime(input_time, now=now)
    assert parsed_datetime == result


def test_get_localtime():
    """Проверка получения локального времени"""
    with patch('datetime.datetime', wraps=datetime.datetime) as dt_mock:
        dt_mock.utcnow.return_value = datetime.datetime(2023, 1, 1, 1, 0)

        local_now = get_localtime('Europe/Moscow')

    assert local_now == pytz.timezone('Europe/Moscow').localize(datetime.datetime(2023, 1, 1, 4, 0))
