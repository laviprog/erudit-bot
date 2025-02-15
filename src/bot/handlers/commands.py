from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from src.bot.messages import get_welcome_message, get_help_message, get_about_message, get_message_with_reply_keyboard, \
    get_profile_message
from src.database import get_db
from src.database.queries import get_user_by_telegram_id

router = Router()


@router.message(CommandStart())
async def start_command(sender: types.Message):
    message = await get_welcome_message()
    await message.send(sender)


@router.message(Command("help"))
async def help_command(sender: types.Message):
    message = await get_help_message()
    await message.send(sender)


@router.message(Command("about"))
async def about_command(sender: types.Message):
    message = await get_about_message()
    await message.send(sender)


@router.message(Command("profile"))
async def profile_command(sender: types.Message):
    telegram_id = sender.from_user.id

    async for session in get_db():
        user = await get_user_by_telegram_id(session, telegram_id)
        message = await get_profile_message(user)
        message_with_reply_keyboard = await get_message_with_reply_keyboard()

        await message.send(sender)
        await message_with_reply_keyboard.send(sender)
