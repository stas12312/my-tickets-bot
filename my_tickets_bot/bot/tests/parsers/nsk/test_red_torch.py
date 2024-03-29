import datetime
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from parsers.nsk import RedTorchParser


@pytest.mark.asyncio
async def test_red_torch_parser():
    """Проверка парсера для театра Красный факел"""
    path = Path(os.path.dirname(os.path.realpath(__file__)), 'files/red-torch.html')
    with path.open(encoding='UTF-8') as file:
        html = file.read()

    parser = RedTorchParser()
    parser.get_data_from_url = AsyncMock(return_value=html)
    parser.get_now = MagicMock(return_value=datetime.datetime(2023, 1, 1))
    events = await parser.get_events()
    assert len(events) == 4

    first_event = events[0]
    assert first_event.url == 'https://red-torch.ru/program/info/troe_v_lodke_ne_schitaya_sobaki/'
    assert first_event.name == 'Трое в лодке, не считая собаки'
    assert first_event.datetime == datetime.datetime(2023, 4, 15, 13, 00)

    second_event = events[1]
    assert second_event.url == 'https://red-torch.ru/program/info/vne_zala/'
    assert second_event.name == 'ВНЕ ЗАЛА'
    assert second_event.datetime == datetime.datetime(2023, 4, 15, 14, 00)

    third_event = events[2]
    assert third_event.url == 'https://red-torch.ru/program/info/syn/'
    assert third_event.name == 'Сын'
    assert third_event.datetime == datetime.datetime(2023, 4, 20, 18, 30)

    fourth_event = events[3]
    assert fourth_event.url == 'https://red-torch.ru/program/info/vysotskiy/'
    assert fourth_event.name == 'Высоцкий'
    assert fourth_event.datetime == datetime.datetime(2023, 4, 20, 20, 00)
