"""
VKontakte Community Wall Sync Worker.
"""

import asyncio
import logging
from aiogram import Bot, types
import vk_api

from bot.core.config import VK_TOKEN, VK_GROUP_ID
from bot.core.database import get_db_connection
from bot.database.groups import get_groups_with_vk_notifications


async def get_vk_news():
    """Fetch recent posts from VK community with graceful offline fallback."""
    if not VK_TOKEN:
        return []
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        posts = vk.wall.get(owner_id=f"-{VK_GROUP_ID}", count=5)
        return posts.get('items', [])
    except Exception as e:
        logging.warning(f"VK API unavailable: {e}")
        return []


async def forward_vk_post_to_telegram(bot: Bot, post, user_id: int):
    """Format and forward VK post to user or group."""
    if not VK_TOKEN:
        return

    try:
        MAX_CAPTION_LENGTH = 1024
        text = post.get('text', '')
        attachments = post.get('attachments', [])
        photos = []
        media = []

        if attachments:
            for attachment in attachments:
                if attachment['type'] == 'photo':
                    sizes = attachment['photo']['sizes']
                    largest_photo = max(sizes, key=lambda x: x['width'] * x['height'])
                    photos.append(largest_photo['url'])
                elif attachment['type'] == 'video':
                    video_data = attachment['video']
                    if 'player' in video_data:
                        if len(attachments) > 1:
                            media.append(types.InputMediaVideo(media=video_data['player'], caption=text if not photos and not media else None))
                            text = ''
                        else:
                            await bot.send_video(user_id, video_data['player'], caption=text)
                            text = ''
                    else:
                        video_link = f"[Посмотреть видео ВКонтакте](https://vk.com/video{video_data['owner_id']}_{video_data['id']})"
                        if len(attachments) > 1:
                            text = (text + "\n" + video_link) if text else video_link
                        else:
                            await bot.send_message(user_id, (text + "\n" + video_link) if text else video_link, parse_mode="Markdown")
                            text = ''

        if len(text) > MAX_CAPTION_LENGTH:
            await bot.send_message(user_id, text)
            text = ''

        if photos:
            if len(photos) == 1 and not media:
                await bot.send_photo(user_id, photos[0], caption=text if text else None)
            else:
                media_group = [types.InputMediaPhoto(media=photo, caption=text if i == 0 and text else None) for i, photo in enumerate(photos)]
                media_group.extend(media)
                await bot.send_media_group(user_id, media_group)
        elif media:
            await bot.send_media_group(user_id, media)
        elif text:
            await bot.send_message(user_id, text)
    except Exception as e:
        logging.error(f"Failed to forward VK post to {user_id}: {e}")


async def check_and_forward_vk_posts(bot: Bot):
    if not VK_TOKEN:
        return

    try:
        posts = await get_vk_news()
        if not posts:
            return

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT post_id FROM sent_vk_posts")
            sent_post_ids = {row[0] for row in cursor.fetchall()}

            new_posts = [p for p in posts if p['id'] not in sent_post_ids]
            if not new_posts:
                return

            cursor.execute("SELECT user_id FROM users WHERE vk_notifications = 1")
            users = cursor.fetchall()
            group_chats = get_groups_with_vk_notifications()

            for post in new_posts:
                post_id = post['id']

                for user in users:
                    try:
                        await forward_vk_post_to_telegram(bot, post, user[0])
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        logging.error(f"Failed to send VK post {post_id} to user {user[0]}: {e}")

                for chat_id in group_chats:
                    try:
                        await forward_vk_post_to_telegram(bot, post, chat_id)
                        await asyncio.sleep(0.05)
                    except Exception as e:
                        logging.error(f"Failed to send VK post {post_id} to group {chat_id}: {e}")

                cursor.execute("INSERT OR IGNORE INTO sent_vk_posts (post_id) VALUES (?)", (post_id,))
                cursor.execute("DELETE FROM sent_vk_posts WHERE post_id NOT IN (SELECT post_id FROM sent_vk_posts ORDER BY sent_at DESC LIMIT 1000)")
                conn.commit()

    except Exception as e:
        logging.error(f"Error in check_and_forward_vk_posts: {e}")


async def check_vk_posts_periodically(bot: Bot):
    """Background polling loop."""
    while True:
        try:
            await check_and_forward_vk_posts(bot)
        except Exception as e:
            logging.error(f"Periodic VK post checking error: {e}")
        await asyncio.sleep(60)
