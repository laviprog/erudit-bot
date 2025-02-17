from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from src.bot.messages import get_application_message, get_message_no_applications, get_message_with_reply_keyboard, \
    get_request_team_name_message, get_start_edit_application_message, get_start_event_registration_message, \
    get_request_team_size_message, get_team_size_value_error_message, get_team_size_error_message
from src.database import get_db
from src.database.models import User, Event, Application, Status
from src.database.queries import get_object_by_id, get_applications_by_user, update_object, \
    get_application_by_event_and_user, create_object, delete_object

router = Router()


@router.message(F.text == "Мои заявки")
async def applications_handler(sender: types.Message):
    telegram_id = sender.from_user.id

    async for session in get_db():
        user = await get_object_by_id(session, User, telegram_id)
        applications = await get_applications_by_user(session, user.id)

        if applications:
            for application in applications:
                event = await get_object_by_id(session, Event, application.event_id)

                message = await get_application_message(application, event)
                await message.send(sender)

        else:
            message = await get_message_no_applications()
            await message.send(sender)

        message = await get_message_with_reply_keyboard()
        await message.send(sender)


class RegisterTeam(StatesGroup):
    team_name = State()
    team_size = State()


@router.callback_query(lambda c: c.data.startswith("register_event:"))
async def register_event(callback: CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split(":")[1])
    telegram_id = callback.from_user.id

    async for session in get_db():
        user = await get_object_by_id(session, User, telegram_id)
        application = await get_application_by_event_and_user(session, event_id, user.id)
        event = await get_object_by_id(session, Event, event_id)

        if application:
            message = await get_application_message(application, event)
            await message.send(callback.message)

        else:
            await state.update_data(event_id=event_id)

            start_registration_message = await get_start_event_registration_message(event)
            request_team_name_message = await get_request_team_name_message()

            await state.set_state(RegisterTeam.team_name)

            await start_registration_message.send(callback.message)
            await request_team_name_message.send(callback.message)

        await callback.answer()


@router.message(StateFilter(RegisterTeam.team_name))
async def process_team_name(sender: types.Message, state: FSMContext):
    team_name = sender.text.strip()

    await state.update_data(team_name=team_name)

    message = await get_request_team_size_message()
    await state.set_state(RegisterTeam.team_size)
    await message.send(sender)


@router.message(StateFilter(RegisterTeam.team_size))
async def process_team_size(sender: types.Message, state: FSMContext):
    try:
        team_size = int(sender.text.strip())
    except ValueError:
        message = await get_team_size_value_error_message()
        await message.send(sender)
        return

    if team_size < 2 or team_size > 10:
        message = await get_team_size_error_message()
        await message.send(sender)
        return

    data = await state.get_data()
    event_id = data["event_id"]
    team_name = data["team_name"]

    async for session in get_db():
        user = await get_object_by_id(session, User, sender.from_user.id)
        event = await get_object_by_id(session, Event, event_id)

        application = await get_application_by_event_and_user(session, event_id, user.id)

        if application:
            application = await update_object(
                session,
                Application,
                application.id,
                team_name=team_name,
                team_size=team_size
            )

        else:
            application = await create_object(
                session,
                Application,
                captain_id=user.id,
                event_id=event_id,
                team_name=team_name,
                team_size=team_size
            )

        message = await get_application_message(application, event)
        message_with_reply_keyboard = await get_message_with_reply_keyboard()

        await message.send(sender)
        await message_with_reply_keyboard.send(sender)
        await state.clear()


@router.callback_query(lambda c: c.data.startswith("delete_application:"))
async def delete_application(callback: CallbackQuery):
    application_id = int(callback.data.split(":")[1])

    async for session in get_db():
        application = await get_object_by_id(session, Application, application_id)

        if application:
            await delete_object(session, Application, application_id)

            # if application.status == Status.APPROVED:
            #     remove_notification(job_id=f"notification_approved_application_{application_id}")

            await callback.message.edit_text("✅ Ваша заявка успешно удалена.")
        else:
            await callback.message.answer("❌ Заявка не найдена.")

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("edit_application:"))
async def edit_application(callback: CallbackQuery, state: FSMContext):
    application_id = int(callback.data.split(":")[1])

    async for session in get_db():
        application = await get_object_by_id(session, Application, application_id)
        event = await get_object_by_id(session, Event, application.event_id)

        if application.status != Status.PENDING:
            await update_object(session, Application, application_id, status=Status.PENDING)

            # if application.status == Status.APPROVED:
            #     remove_notification(job_id=f"notification_approved_application_{application_id}")

        await state.update_data(event_id=event.id)

        start_edit_message = await get_start_edit_application_message(event)
        request_team_name_message = await get_request_team_name_message()

        await state.update_data(application_id=application_id)
        await state.set_state(RegisterTeam.team_name)

        await start_edit_message.send(callback.message)
        await request_team_name_message.send(callback.message)
        await callback.answer()
