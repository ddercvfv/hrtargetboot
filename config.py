import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv не установлен. Используйте переменные окружения системы или установите зависимости: pip install -r requirements.txt")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # ID администратора для рассылки

# Ссылки и данные
REVIEWS_CHANNEL = "https://t.me/estasiacars"
COURSE_POST_LINK = "https://t.me/cnchange/185"
YANDEX_MAPS_LINK = "https://yandex.ru/maps/org/cn_bridge/37529426458/reviews/?from=mapframe&ll=37.625325%2C55.695281&source=mapframe&tab=reviews&um=constructor%3Ab4c9ca86698ace75ba702643723eee2c41f695b5c08a869315a7e1a26937c4bb&utm_source=mapframe&z=15.4"
TELEGRAM = "https://t.me/cnbridgeru"
INSTARGRAM = "https://www.instagram.com/cn.bridge"
VK = "https://vk.com/cnbridge"
DZEN = "https://dzen.ru/id/67485ea7f18c29468e3620c4?share_to=link"

# Социальные сети
SOCIAL_LINKS = {
    "telegram": "https://t.me/cnbridgeru",
    "instagram": "https://www.instagram.com/cn.bridge?igsh=NDRtanJ0YWN5eGs2",
    "vk": "https://vk.com/cnbridge",
    "zen": "https://dzen.ru/id/67485ea7f18c29468e3620c4?share_to=link"
}
