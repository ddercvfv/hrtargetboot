from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import YANDEX_MAPS_LINK, SOCIAL_LINKS, COURSE_POST_LINK

def get_main_menu():
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📊 Получить расчёт"),
        KeyboardButton(text="🛠 Услуги"),
        KeyboardButton(text="ℹ️ О нас"),
        KeyboardButton(text="💬 Отзывы"),
        KeyboardButton(text="📚 Полезные материалы"),
        KeyboardButton(text="❓ FAQ")
    )
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_services_menu():
    """Меню услуг"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🚚 Доставка грузов"),
        KeyboardButton(text="💰 Перевод денег"),
        KeyboardButton(text="🛒 Выкуп товара"),
        KeyboardButton(text="🔍 Поиск поставщика"),
        KeyboardButton(text="📦 Заказ образцов"),
        KeyboardButton(text="📋 Фулфилмент"),
        KeyboardButton(text="📜 Сертификация"),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_delivery_methods():
    """Способы доставки"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🚗 Авто"),
        KeyboardButton(text="🚛 Автоэкспресс"),
        KeyboardButton(text="🚂 ЖД"),
        KeyboardButton(text="✈️ Авиа"),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_contact_keyboard():
    """Клавиатура для отправки контакта"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📱 Поделиться контактом", request_contact=True),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_back_to_menu():
    """Кнопка назад в меню"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Назад в меню"))
    return builder.as_markup(resize_keyboard=True)

def get_about_us_inline():
    """Инлайн клавиатура для раздела О нас"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🌐 Наш сайт", url="https://cnbridge.ru"),
        InlineKeyboardButton(text="🏢 Карточка организации", callback_data="company_card"),
        InlineKeyboardButton(text="📱 Наши соцсети", callback_data="social_networks")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_social_networks():
    """Социальные сети"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📱 Telegram", url=SOCIAL_LINKS["telegram"]),
        InlineKeyboardButton(text="📸 Instagram", url=SOCIAL_LINKS["instagram"]),
        InlineKeyboardButton(text="🌐 VK", url=SOCIAL_LINKS["vk"]),
        InlineKeyboardButton(text="📰 Дзен", url=SOCIAL_LINKS["zen"])
    )
    builder.adjust(2, 2)
    return builder.as_markup()

def get_materials_menu():
    """Меню полезных материалов"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📘 3 ошибки селлера"),
        KeyboardButton(text="📗 Как выйти на маркетплейсы в 2025"),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(1, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def get_service_action(service_name: str):
    """Кнопки для услуг"""
    builder = InlineKeyboardBuilder()
    if service_name == "Перевод денег":
        builder.add(
            InlineKeyboardButton(text="📈 Курс", url=COURSE_POST_LINK),
            InlineKeyboardButton(text="📞 Получить услугу", callback_data="get_service_Перевод денег")
        )
        builder.adjust(2)
    else:
        service_callback = service_name.replace(" ", "_")
        builder.add(
            InlineKeyboardButton(text="📞 Получить услугу", callback_data=f"get_service_{service_callback}")
        )
        builder.adjust(1)
    return builder.as_markup()

def get_admin_keyboard():
    """Админ клавиатура"""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📢 Создать рассылку"),
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)
