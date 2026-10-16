"""
Announcement & Schedule Broadcast Service.
"""

import asyncio
import logging
from aiogram import Bot

from bot.core.database import get_db_connection
from bot.database.groups import get_all_groups, get_groups_with_schedule_notifications


async def send_announcement(bot: Bot, text: str, media=None):
    """Broadcast announcement with optional photo or video to all users and groups."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()

            for user in users:
                try:
                    if media:
                        if media['type'] == 'photo':
                            await bot.send_photo(user[0], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                        elif media['type'] == 'video':
                            await bot.send_video(user[0], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                    else:
                        await bot.send_message(user[0], f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                    await asyncio.sleep(0.05)
                except Exception as e:
                    logging.warning(f"Failed to send announcement to user {user[0]}: {e}")

        # Send to groups and channels
        groups = get_all_groups()
        for group in groups:
            try:
                if media:
                    if media['type'] == 'photo':
                        await bot.send_photo(group['chat_id'], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                    elif media['type'] == 'video':
                        await bot.send_video(group['chat_id'], media['file_id'], caption=f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                else:
                    await bot.send_message(group['chat_id'], f"📢 ОБЪЯВЛЕНИЕ:\n\n{text}")
                await asyncio.sleep(0.05)
            except Exception as e:
                logging.warning(f"Failed to send announcement to group {group['chat_id']}: {e}")

    except Exception as e:
        logging.error(f"Error in send_announcement: {e}")


async def send_schedule_notification(bot: Bot, date: str, is_update: bool = False):
    """Notify users and groups when a schedule is added or updated."""
    try:
        action = "обновлено" if is_update else "добавлено"
        message = f"📅 Расписание на {date} было {action}!"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE schedule_notifications = 1')
            users = cursor.fetchall()

            for user in users:
                try:
                    await bot.send_message(user[0], message)
                    await asyncio.sleep(0.05)
                except Exception as e:
                    logging.warning(f"Error sending schedule alert to {user[0]}: {e}")

        groups = get_groups_with_schedule_notifications()
        for chat_id in groups:
            try:
                await bot.send_message(chat_id, message)
                await asyncio.sleep(0.05)
            except Exception as e:
                logging.warning(f"Error sending schedule alert to group {chat_id}: {e}")

    except Exception as e:
        logging.error(f"Error in send_schedule_notification: {e}")
