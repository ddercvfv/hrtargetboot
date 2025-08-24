import aiosqlite
import asyncio
from typing import List, Optional

DATABASE_PATH = "bot_database.db"

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                contact_shared BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_name TEXT,
                cargo_name TEXT,
                cargo_volume TEXT,
                cargo_weight TEXT,
                delivery_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.commit()

async def add_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Добавление пользователя в базу данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))
        await db.commit()

async def update_user_contact(user_id: int, phone_number: str):
    """Обновление контакта пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE users SET phone_number = ?, contact_shared = TRUE
            WHERE user_id = ?
        """, (phone_number, user_id))
        await db.commit()

async def is_contact_shared(user_id: int) -> bool:
    """Проверка, поделился ли пользователь контактом"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT contact_shared FROM users WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else False

async def add_lead(user_id: int, service_name: str, **kwargs):
    """Добавление лида"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO leads (user_id, service_name, cargo_name, cargo_volume, cargo_weight, delivery_method)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, service_name, kwargs.get('cargo_name'), kwargs.get('cargo_volume'), 
              kwargs.get('cargo_weight'), kwargs.get('delivery_method')))
        await db.commit()

async def get_all_users() -> List[int]:
    """Получение всех пользователей для рассылки"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()
        return [user[0] for user in users]

async def get_user_info(user_id: int) -> Optional[dict]:
    """Получение информации о пользователе"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT username, first_name, last_name, phone_number
            FROM users WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        if result:
            return {
                'username': result[0],
                'first_name': result[1],
                'last_name': result[2],
                'phone_number': result[3]
            }
        return None

async def get_user_phone(user_id: int) -> Optional[str]:
    """Получение телефона пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT phone_number FROM users WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else None
