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


async def get_reply_keyboard_start_registration():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Начать регистрацию 📝")
            ]
        ],
        resize_keyboard=True,
    )


async def get_reply_keyboard_phone_number():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Отправить номер телефона", request_contact=True)
            ]
        ],
        resize_keyboard=True,
    )


async def get_inline_keyboard_for_event_registration(event_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Зарегистрироваться",
                    callback_data=f"register_event:{event_id}"
                )
            ],
        ]
    )


async def get_inline_keyboard_for_application_management(application_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить заявку", callback_data=f"edit_application:{application_id}")],
        [InlineKeyboardButton(text="❌ Удалить заявку", callback_data=f"delete_application:{application_id}")],
    ])
