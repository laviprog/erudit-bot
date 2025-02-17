from aiogram import Dispatcher

from src.bot.handlers.commands import router as command_router
from src.bot.handlers.profile import router as profile_router
from src.bot.handlers.events import router as events_router
from src.bot.handlers.applications import router as applications_router


def register_handlers(dp: Dispatcher):
    dp.include_router(command_router)
    dp.include_router(profile_router)
    dp.include_router(events_router)
    dp.include_router(applications_router)
