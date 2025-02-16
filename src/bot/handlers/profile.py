from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.bot.messages import get_start_registration_message, get_phone_request_message, get_phone_error_message, \
    get_profile_message, get_message_with_reply_keyboard, get_start_edit_profile_message
from src.database import get_db
from src.database.models import User
from src.database.queries import create_object, update_object, get_object_by_id

router = Router()


class UserInfo(StatesGroup):
    full_name = State()
    phone_number = State()


@router.message(F.text == "Начать регистрацию 📝")
async def start_registration(sender: types.Message, state: FSMContext):
    telegram_id = sender.from_user.id
    username = sender.from_user.username

    async for session in get_db():
        user = await get_object_by_id(session, User, telegram_id)
        message = await get_start_registration_message(user)

        if not user:
            await create_object(
                session,
                User,
                id=telegram_id,
                username=username
            )
            await state.set_state(UserInfo.full_name)

        await message.send(sender)


@router.message(StateFilter(UserInfo.full_name))
async def process_full_name(sender: types.Message, state: FSMContext):
    full_name = sender.text
    telegram_id = sender.from_user.id

    async for session in get_db():
        await update_object(session, User, telegram_id, full_name=full_name)

    await state.set_state(UserInfo.phone_number)

    message = await get_phone_request_message()
    await message.send(sender)


@router.message(StateFilter(UserInfo.phone_number))
async def process_phone_number(sender: types.Message, state: FSMContext):
    if not sender.contact:
        message = await get_phone_error_message()
        await message.send(sender)
        return

    phone_number = sender.contact.phone_number
    telegram_id = sender.from_user.id

    async for session in get_db():
        updated_user = await update_object(session, User, telegram_id, phone_number=phone_number)

        message = await get_profile_message(updated_user)
        message_with_reply_keyboard = await get_message_with_reply_keyboard()
        await message.send(sender)
        await message_with_reply_keyboard.send(sender)
        await state.clear()


@router.callback_query(lambda c: c.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserInfo.full_name)

    message = await get_start_edit_profile_message()
    await message.send(callback.message)

    await callback.answer()
