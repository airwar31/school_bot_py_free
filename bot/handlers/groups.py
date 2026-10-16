"""
Group Chat Management & Bot Membership Events Router.
"""

import logging
from aiogram import Router, Bot, F, types
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER

from bot.database.groups import add_group, remove_group, get_group_settings, toggle_group_vk_notifications

groups_router = Router(name="groups")


@groups_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_group(event: types.ChatMemberUpdated):
    chat = event.chat
    add_group(chat.id, chat.type, chat.title)
    logging.info(f"Bot added to group {chat.title} ({chat.id})")


@groups_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER))
async def bot_removed_from_group(event: types.ChatMemberUpdated):
    chat = event.chat
    remove_group(chat.id)
    logging.info(f"Bot removed from group {chat.title} ({chat.id})")


@groups_router.message(Command("settings"), F.chat.type.in_(["group", "supergroup"]))
async def group_settings_command(message: types.Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ['creator', 'administrator']:
        await message.reply("❌ Только администраторы беседы могут настраивать бота.")
        return

    settings = get_group_settings(message.chat.id)
    if not settings:
        await message.reply("❌ Беседа не найдена в базе данных.")
        return

    vk_status = "🔔 Включены" if settings.get('vk_notifications') else "🔕 Отключены"
    await message.reply(
        f"⚙️ <b>Настройки группы '{message.chat.title}':</b>\n\n"
        f"📰 VK Новости: {vk_status}\n\n"
        f"Используйте /toggle_vk для переключения уведомлений.",
        parse_mode="HTML"
    )


@groups_router.message(Command("toggle_vk"), F.chat.type.in_(["group", "supergroup"]))
async def toggle_vk_command(message: types.Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ['creator', 'administrator']:
        await message.reply("❌ Только администраторы могут переключать уведомления.")
        return

    settings = get_group_settings(message.chat.id)
    if not settings:
        return

    new_val = not settings.get('vk_notifications', True)
    toggle_group_vk_notifications(message.chat.id, new_val)
    status_str = "включены" if new_val else "отключены"
    await message.reply(f"✅ VK уведомления для группы {status_str}!")
