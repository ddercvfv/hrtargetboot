import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message

from config import ADMIN_ID
import database as db

async def send_lead_to_admin(bot: Bot, user_id: int, service_name: str, **kwargs):
    """Отправка лида администратору"""
    user_info = await db.get_user_info(user_id)
    
    lead_text = f"""
🔥 <b>Новый лид!</b>

👤 <b>Клиент:</b>
• Имя: {user_info['first_name'] or 'не указано'} {user_info['last_name'] or ''}
• Username: @{user_info['username'] or 'не указан'}
• Телефон: {user_info['phone_number'] or 'не указан'}
• ID: {user_id}

🛠 <b>Услуга:</b> {service_name}
    """
    
    # Добавляем дополнительную информацию если есть
    if kwargs.get('cargo_name'):
        lead_text += f"\n📦 <b>Груз:</b> {kwargs['cargo_name']}"
    if kwargs.get('cargo_volume'):
        lead_text += f"\n📏 <b>Объём:</b> {kwargs['cargo_volume']}"
    if kwargs.get('cargo_weight'):
        lead_text += f"\n⚖️ <b>Вес:</b> {kwargs['cargo_weight']}"
    if kwargs.get('delivery_method'):
        lead_text += f"\n🚚 <b>Способ доставки:</b> {kwargs['delivery_method']}"
    
    try:
        await bot.send_message(ADMIN_ID, lead_text)
    except Exception as e:
        print(f"Ошибка отправки лида админу: {e}")

async def broadcast_message(bot: Bot, user_ids: list, message: Message) -> int:
    """Рассылка сообщения пользователям (поддерживает текст, фото, видео и другие типы)"""
    success_count = 0
    
    for user_id in user_ids:
        try:
            # Определяем тип сообщения и отправляем соответствующим методом
            if message.photo:
                # Отправляем фото с подписью
                await bot.send_photo(
                    user_id, 
                    message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.video:
                # Отправляем видео с подписью
                await bot.send_video(
                    user_id,
                    message.video.file_id,
                    caption=message.caption
                )
            elif message.document:
                # Отправляем документ с подписью
                await bot.send_document(
                    user_id,
                    message.document.file_id,
                    caption=message.caption
                )
            elif message.animation:
                # Отправляем GIF с подписью
                await bot.send_animation(
                    user_id,
                    message.animation.file_id,
                    caption=message.caption
                )
            elif message.voice:
                # Отправляем голосовое сообщение
                await bot.send_voice(
                    user_id,
                    message.voice.file_id,
                    caption=message.caption
                )
            elif message.video_note:
                # Отправляем видеосообщение
                await bot.send_video_note(
                    user_id,
                    message.video_note.file_id
                )
            elif message.sticker:
                # Отправляем стикер
                await bot.send_sticker(
                    user_id,
                    message.sticker.file_id
                )
            elif message.text:
                # Отправляем текстовое сообщение
                await bot.send_message(user_id, message.text)
            else:
                # Если тип сообщения не поддерживается, пропускаем
                continue
                
            success_count += 1
            await asyncio.sleep(0.05)  # Задержка между отправками
            
        except (TelegramBadRequest, TelegramForbiddenError):
            # Пользователь заблокировал бота или удалил аккаунт
            continue
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
            continue
    
    return success_count
