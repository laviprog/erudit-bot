from datetime import datetime

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.keyboards import get_reply_keyboard, get_inline_keyboard_for_profile_management, \
    get_reply_keyboard_start_registration, get_reply_keyboard_phone_number, get_inline_keyboard_for_event_registration, \
    get_inline_keyboard_for_application_management
from src.database.models import User, Event, Application, Status


class Message:

    def __init__(
            self,
            text: str,
            keyboard: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove = None,
            image_url: str = None,
    ):
        self.text = text
        self.keyboard = keyboard
        self.image_url = image_url

    async def send(self, sender: types.Message) -> None:
        if self.image_url:
            await sender.answer_photo(
                photo=self.image_url,
                caption=self.text,
                reply_markup=self.keyboard,
            )

        else:
            await sender.answer(
                self.text,
                reply_markup=self.keyboard,
            )

    async def edit(self, sender: types.Message) -> None:
        await sender.edit_text(
            self.text,
        )

    def to_dict(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if value is not None}


async def get_welcome_message(user: User) -> Message:
    if user:
        return Message(
            text=(
                "Welcome text for active user"
            ),
            keyboard=await get_reply_keyboard()
        )

    return Message(
        text=(
            "Welcome text"
        ),
        keyboard=await get_reply_keyboard_start_registration()
    )


async def get_help_message() -> Message:
    return Message(
        text=(
            "Текст помощи и описание команд"
        ),
        keyboard=await get_reply_keyboard(),
    )


async def get_about_message() -> Message:
    return Message(
        text=(
            "Текст о боте и его создателях"
        ),
        keyboard=await get_reply_keyboard(),
    )


async def get_profile_message(user: User) -> Message:
    if not user:
        return Message(
            text=(
                "Ошибка: пользователь не найден"
            ),
        )

    return Message(
        text=(
            f"👤 Профиль пользователя:\n"
            f"Имя: {user.full_name}\n"
            f"Телефон: {user.phone_number or 'Не указан'}"
        ),
        keyboard=await get_inline_keyboard_for_profile_management()
    )


async def get_message_with_reply_keyboard(
        text: str = "Для продолжения работы нажмите на одну из кнопок или команд"
) -> Message:
    return Message(
        text=text,
        keyboard=await get_reply_keyboard()
    )


async def get_start_registration_message(user):
    if user:
        return Message(
            text=(
                "Вы уже зарегистрированы, выберите команду из меню или одну из кнопок ниже ↓ "
            ),
        )

    return Message(
        text=(
            "Начнем регистрацию!\nВведите свое полное имя (например, Иван Иванов)"
        ),
        keyboard=ReplyKeyboardRemove(),
    )


async def get_phone_request_message():
    return Message(
        text=(
            "Отправьте свой номер телефона используя кнопку ниже"
        ),
        keyboard=await get_reply_keyboard_phone_number(),
    )


async def get_phone_error_message() -> Message:
    return Message(
        text=(
            "Отправьте свой номер телефона используя кнопку ниже"
        ),
    )


async def get_start_edit_profile_message() -> Message:
    return Message(
        text=(
            "Начнем изменение профиля\nВведите свое полное имя (например, Иван Иванов)"
        ),
        keyboard=ReplyKeyboardRemove(),
    )


async def get_event_text(event: Event) -> str:
    return (
        f"📅 {event.event_time.strftime('%d.%m.%Y %H:%M')} - {event.title}\n"
        f"📍 {event.location}\n"
        f"📝 {event.description or 'Без описания'}"
    )


async def get_event_message(event: Event = None) -> Message:
    if not event:
        return Message(
            text=(
                "К сожалению, событий нет. Мы обязательно вам сообщим о новых событиях!"
            ),
        )

    return Message(
        text=await get_event_text(event),
        keyboard=await get_inline_keyboard_for_event_registration(event.id),
        image_url=event.image_url,
    )


async def get_application_text(application: Application) -> str:
    STATUS_LABELS = {
        Status.APPROVED: "✅ Подтверждена",
        Status.PENDING: "⏳ Ожидает подтверждения",
        Status.DECLINED: "❌ Отклонена",
    }
    status = STATUS_LABELS.get(application.status, "⚠ Неизвестный статус")

    return (
        f"📌 Ваша заявка на это событие:\nНазвание команды: {application.team_name}\n"
        f"Количество участников: {application.team_size}\nСтатус: {status}"
    )


async def get_application_message(application: Application, event: Event = None) -> Message:
    text = await get_application_text(application)

    if event:
        if event.end_registration_time < datetime.now():
            return Message(
                text=(
                    "К сожалению, регистрация уже закончилась, свяжитесь с организаторами"
                ),
            )

        else:
            event_text = await get_event_text(event)
            text = event_text + '\n\n' + text

    return Message(
        text,
        await get_inline_keyboard_for_application_management(application.id),
    )


async def get_message_no_applications() -> Message:
    return Message(
        text=(
            "На текущий момент у вас нет заявок на события"
        ),
        keyboard=await get_reply_keyboard(),
    )


async def get_start_event_registration_message(event: Event) -> Message:
    return Message(
        text=(
            f"Начинаем регистрацию на событие: {event.title}"
        ),
    )


async def get_request_team_name_message() -> Message:
    return Message(
        text=(
            "Введите название вашей команды"
        ),
        keyboard=ReplyKeyboardRemove()
    )


async def get_request_team_size_message() -> Message:
    return Message(
        text=(
            "Сколько человек в вашей команде? (от 2 до 10 участников)"
        ),
    )


async def get_team_size_value_error_message() -> Message:
    return Message(
        text=(
            "🚫 Введите число - количество участников вашей команды. Попробуйте снова"
        ),
    )


async def get_team_size_error_message() -> Message:
    return Message(
        text=(
            "🚫 Количество участников должно быть от 2 до 10. Попробуйте снова"
        ),
    )


async def get_start_edit_application_message(event: Event) -> Message:
    return Message(
        text=(
            f"Приступаем к изменения заявки на событие: {event.title}"
        ),
    )
