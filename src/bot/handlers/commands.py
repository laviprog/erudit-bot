from aiogram import Router, types
from aiogram.filters import CommandStart

from src.bot.messages import get_welcome_message

router = Router()


@router.message(CommandStart())
async def start_command(sender: types.Message):
    message = await get_welcome_message()
    await message.send(sender)
