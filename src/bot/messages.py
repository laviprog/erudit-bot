from aiogram import types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove


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


async def get_welcome_message():
    return Message(
        "Welcome text"
    )
