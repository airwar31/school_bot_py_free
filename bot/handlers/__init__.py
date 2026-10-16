"""
Centralized Router Assembler
Connects all domain-specific routers to the aiogram Dispatcher.
"""

from aiogram import Dispatcher

from .common import common_router
from .registration import registration_router
from .profile import profile_router
from .schedule import schedule_router
from .announcements import announcements_router
from .events import events_router
from .feedback import feedback_router
from .groups import groups_router
from .vk import vk_router
from .cop import cop_router


def setup_routers(dp: Dispatcher):
    """Registers all domain feature routers."""
    dp.include_router(common_router)
    dp.include_router(registration_router)
    dp.include_router(profile_router)
    dp.include_router(schedule_router)
    dp.include_router(announcements_router)
    dp.include_router(events_router)
    dp.include_router(feedback_router)
    dp.include_router(groups_router)
    dp.include_router(vk_router)
    dp.include_router(cop_router)
