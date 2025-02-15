from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.keyboards import get_reply_keyboard, get_inline_keyboard_for_profile_management
from src.database.models import User


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


async def get_welcome_message() -> Message:
    return Message(
        "Welcome text"
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
