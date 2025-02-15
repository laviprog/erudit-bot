from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


async def get_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ближайшие события"),
                KeyboardButton(text="Мои заявки"),
            ]
        ],
        resize_keyboard=True,
    )


async def get_inline_keyboard_for_profile_management():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить данные", callback_data=f"edit_profile")],
    ])

