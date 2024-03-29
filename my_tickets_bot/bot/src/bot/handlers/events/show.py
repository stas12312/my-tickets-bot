"""Отображение мероприятия"""
import datetime

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Text

from bot.buttons import MainMenu
from bot.callbacks import EventCallback, EntityAction, PaginationCallback
from bot.keyboards.event import get_actions_for_event, get_actions_for_edit_event, get_event_list_keyboard, \
    EventListMode
from bot.messages.event import send_event_card, make_event_message, get_event_calendar_url
from bot.paginators.event import EventPaginator
from services.config import Config
from services.profile import duration
from services.repositories import Repo


async def show_edits_handler(
        query: types.CallbackQuery,
        callback_data: EventCallback,
):
    """Отображению меню настроек"""
    event_id = callback_data.event_id
    keyboard = get_actions_for_edit_event(event_id)
    await query.message.edit_reply_markup(reply_markup=keyboard)


async def show_event_handler(
        query: types.CallbackQuery,
        callback_data: EventCallback,
        config: Config,
        repo: Repo,
):
    """Отображение события"""
    event_id = callback_data.event_id
    event = await repo.event.get(query.from_user.id, event_id)
    tickets = await repo.ticket.list_for_event(query.from_user.id, event_id)

    calendar_url = get_event_calendar_url(config.host, event.uuid)
    keyboard = get_actions_for_event(event, tickets, calendar_url)
    event_message = make_event_message(event)
    await query.message.edit_text(
        text=event_message,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def my_events_handler(
        message: types.Message,
        repo: Repo,
):
    """Отображения событий пользователя"""
    msg, keyboard = await get_message_with_keyboard(message.from_user.id, 0, EventListMode.PLANNED, repo)
    await message.answer(msg, disable_web_page_preview=True, reply_markup=keyboard)


async def my_events_with_page_handler(
        query: types.CallbackQuery,
        callback_data: PaginationCallback,
        repo: Repo,
):
    """Обработка переключения страницы"""
    await query.answer()
    if callback_data.page is None:
        return
    mode = EventListMode(callback_data.mode)
    msg, keyboard = await get_message_with_keyboard(query.from_user.id, callback_data.page, mode, repo)
    await query.message.edit_text(msg, disable_web_page_preview=True, reply_markup=keyboard)


@duration
async def get_message_with_keyboard(
        user_id: int,
        page: int,
        mode: EventListMode,
        repo: Repo,
) -> tuple[str, types.InlineKeyboardMarkup]:
    """Получение сообщения и клавиатуры для списка мероприятий"""
    # Будем показывать прошедшие мероприятия в течение дня
    actual_time = datetime.datetime.now() - datetime.timedelta(hours=24)

    event_paginator = EventPaginator(
        repo=repo,
        user_id=user_id,
        is_actual=mode == EventListMode.PLANNED,
        actual_datetime=actual_time,
        number=page,
        size=5,
    )

    events = await event_paginator.get_data()
    events_message = [
        make_event_message(
            event=event,
            with_command=True,
            with_address=False,
            with_left_time=False,
        )
        for event
        in events
    ]

    keyboard = await get_event_list_keyboard(event_paginator, mode)

    msg = '\n\n'.join(events_message) or 'У вас нет мероприятий'

    return msg, keyboard


async def event_card_handler(
        message: types.Message,
        bot: Bot,
        config: Config,
        repo: Repo,
):
    """Получение карточки билета"""
    event_id = int(message.text.split('_')[1])
    await send_event_card(bot, message.from_user.id, event_id, repo, config)
    await message.delete()


router = Router()
router.message.register(my_events_handler, Text(text=MainMenu.MY_EVENTS))

router.message.register(event_card_handler, Text(startswith='/event_'))
router.callback_query.register(show_edits_handler, EventCallback.filter(F.action == EntityAction.EDIT))
router.callback_query.register(show_event_handler, EventCallback.filter(F.action == EntityAction.SHOW))
router.callback_query.register(my_events_with_page_handler, PaginationCallback.filter(F.object_name == 'EVENT'))
