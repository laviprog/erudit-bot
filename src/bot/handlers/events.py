from aiogram import Router, F, types

from src.bot.messages import get_message_with_reply_keyboard, get_event_message
from src.database import get_db
from src.database.queries import get_current_events

router = Router()


@router.message(F.text == "Ближайшие события")
async def events_handler(sender: types.Message):
    async for session in get_db():
        events = await get_current_events(session)

        if not events:
            message = await get_event_message()
            await message.send(sender)

        else:
            for event in events:
                message = await get_event_message(event)

                await message.send(sender)

        message = await get_message_with_reply_keyboard()
        await message.send(sender)
