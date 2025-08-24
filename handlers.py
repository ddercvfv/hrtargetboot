from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os

import database as db
import keyboards as kb
from config import ADMIN_ID, REVIEWS_CHANNEL, COURSE_POST_LINK, SOCIAL_LINKS
from admin import send_lead_to_admin, broadcast_message

router = Router()

class CalculationStates(StatesGroup):
    waiting_cargo_name = State()
    waiting_cargo_volume = State()
    waiting_cargo_weight = State()
    waiting_contact = State()

class DeliveryStates(StatesGroup):
    waiting_method = State()
    waiting_contact = State()

class BroadcastStates(StatesGroup):
    waiting_message = State()

class ServiceStates(StatesGroup):
    waiting_contact = State()
    waiting_name = State()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    welcome_text = """
🎉 <b>Добро пожаловать!</b>

Я помогу вам с логистикой и доставкой грузов из Китая.

Выберите нужный раздел в меню ниже:
    """
    
    try:
        photo_path = get_file_path("welcome.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=welcome_text, reply_markup=kb.get_main_menu())
    except FileNotFoundError:
        await message.answer(welcome_text, reply_markup=kb.get_main_menu())

# Админ команды
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer("🔧 <b>Админ-панель</b>", reply_markup=kb.get_admin_keyboard())

@router.message(F.text == "📢 Создать рассылку")
async def create_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("📝 Отправьте сообщение для рассылки:")
    await state.set_state(BroadcastStates.waiting_message)

@router.message(StateFilter(BroadcastStates.waiting_message))
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = await db.get_all_users()
    success_count = await broadcast_message(message.bot, users, message)
    
    await message.answer(f"✅ Рассылка завершена!\nОтправлено: {success_count} из {len(users)} пользователей")
    await state.clear()

@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    users = await db.get_all_users()
    await message.answer(f"📊 <b>Статистика бота:</b>\n\n👥 Всего пользователей: {len(users)}")

# Главное меню
@router.message(F.text == "⬅️ Назад в меню")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Главное меню:", reply_markup=kb.get_main_menu())

# Получить расчёт
@router.message(F.text == "📊 Получить расчёт")
async def get_calculation(message: Message, state: FSMContext):
    await message.answer("📦 Введите название груза (его описание):", reply_markup=kb.get_back_to_menu())
    await state.set_state(CalculationStates.waiting_cargo_name)

@router.message(StateFilter(CalculationStates.waiting_cargo_name))
async def process_cargo_name(message: Message, state: FSMContext):
    await state.update_data(cargo_name=message.text)
    await message.answer("📏 Введите объём груза:", reply_markup=kb.get_back_to_menu())
    await state.set_state(CalculationStates.waiting_cargo_volume)

@router.message(StateFilter(CalculationStates.waiting_cargo_volume))
async def process_cargo_volume(message: Message, state: FSMContext):
    await state.update_data(cargo_volume=message.text)
    await message.answer("⚖️ Введите вес груза:", reply_markup=kb.get_back_to_menu())
    await state.set_state(CalculationStates.waiting_cargo_weight)

@router.message(StateFilter(CalculationStates.waiting_cargo_weight))
async def process_cargo_weight(message: Message, state: FSMContext):
    await state.update_data(cargo_weight=message.text)
    
    # Проверяем, поделился ли пользователь контактом
    contact_shared = await db.is_contact_shared(message.from_user.id)
    
    if not contact_shared:
        await message.answer("📱 Для получения расчёта поделитесь контактом:", reply_markup=kb.get_contact_keyboard())
        await state.set_state(CalculationStates.waiting_contact)
    else:
        # Отправляем данные админу
        data = await state.get_data()
        await send_lead_to_admin(message.bot, message.from_user.id, "Расчёт доставки", **data)
        await db.add_lead(message.from_user.id, "Расчёт доставки", **data)
        
        await message.answer("✅ Ваш запрос отправлен! Мы свяжемся с вами в ближайшее время.", 
                           reply_markup=kb.get_main_menu())
        await state.clear()

@router.message(StateFilter(CalculationStates.waiting_contact))
async def process_cargo_contact(message: Message, state: FSMContext):
    contact: Contact = message.contact
    
    # Сохраняем контакт в базу данных
    await db.update_user_contact(message.from_user.id, contact.phone_number)
    
    # Отправляем данные админу
    data = await state.get_data()
    data['contact'] = contact.phone_number
    await send_lead_to_admin(message.bot, message.from_user.id, "Расчёт доставки", **data)
    await db.add_lead(message.from_user.id, "Расчёт доставки", **data)
    
    await message.answer("✅ Ваш запрос отправлен! Мы свяжемся с вами в ближайшее время.", 
                           reply_markup=kb.get_main_menu())
    await state.clear()

# Услуги
@router.message(F.text == "🛠 Услуги")
async def services_menu(message: Message):
    await message.answer("🛠 <b>Наши услуги:</b>\n\nВыберите интересующую услугу:", 
                        reply_markup=kb.get_services_menu())

# Доставка грузов
@router.message(F.text == "🚚 Доставка грузов")
async def delivery_service(message: Message):
    text = """
🚚 <b>Доставка грузов из Китая</b>

Мы предлагаем различные способы доставки:
• Автомобильная доставка
• Автоэкспресс
• Железнодорожная доставка  
• Авиадоставка

Выберите подходящий способ доставки или получите консультацию.
    """
    
    try:
        photo_path = get_file_path("delivery.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Доставка грузов"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Доставка грузов"))

# Перевод денег
@router.message(F.text == "💰 Перевод денег")
async def money_transfer(message: Message):
    text = """
💰 <b>Перевод денег в Китай</b>

Быстрый и безопасный перевод денег в Китай по выгодному курсу.

• Минимальные комиссии
• Быстрое зачисление
• Безопасные переводы
    """
    
    try:
        photo_path = get_file_path("money.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Перевод денег"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Перевод денег"))
    
    await message.answer("⬅️ Для возврата в меню нажмите кнопку ниже:", reply_markup=kb.get_back_to_menu())

# Остальные услуги (аналогично)
@router.message(F.text == "🛒 Выкуп товара")
async def product_buyout(message: Message):
    text = """
🛒 <b>Выкуп товара в Китае</b>

Поможем выкупить товар у китайских поставщиков:
• Проверка качества
• Безопасная оплата
• Контроль процесса
    """
    try:
        photo_path = get_file_path("buyout.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Выкуп товара"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Выкуп товара"))

@router.message(F.text == "🔍 Поиск поставщика")
async def supplier_search(message: Message):
    text = """
🔍 <b>Поиск поставщика</b>

Найдём надёжного поставщика для вашего товара:
• Проверка репутации
• Сравнение цен
• Контроль качества
    """
    try:
        photo_path = get_file_path("supplier.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Поиск поставщика"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Поиск поставщика"))

@router.message(F.text == "📦 Заказ образцов")
async def sample_order(message: Message):
    text = """
📦 <b>Заказ образцов</b>

Закажем образцы товаров для проверки качества:
• Быстрая доставка образцов
• Проверка качества
• Детальные фото и видео
    """
    try:
        photo_path = get_file_path("samples.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Заказ образцов"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Заказ образцов"))

@router.message(F.text == "📋 Фулфилмент")
async def fulfillment(message: Message):
    text = """
📋 <b>Фулфилмент</b>

Полный цикл обработки заказов:
• Хранение товаров
• Упаковка и отправка
• Обработка возвратов
    """
    try:
        photo_path = get_file_path("fulfillment.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Фулфилмент"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Фулфилмент"))

@router.message(F.text == "📜 Сертификация")
async def certification(message: Message):
    text = """
📜 <b>Сертификация товаров</b>

Поможем получить необходимые сертификаты:
• Сертификаты соответствия
• Декларации
• Разрешительные документы
    """
    try:
        photo_path = get_file_path("certification.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_service_action("Сертификация"))
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_service_action("Сертификация"))

# О нас
@router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    text = """
ℹ️ <b>О нашей компании</b>

Мы - надёжный партнёр в сфере логистики и доставки грузов из Китая.

🏢 Опыт работы более 10 лет
🌍 Офисы в России и Китае  
⚡ Быстрая доставка
💯 Гарантия качества услуг
    """
    
    try:
        photo_path = get_file_path("about.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_about_us_inline())
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_about_us_inline())
    
    await message.answer("⬅️ Для возврата в меню нажмите кнопку ниже:", reply_markup=kb.get_back_to_menu())

# Отзывы
@router.message(F.text == "💬 Отзывы")
async def reviews(message: Message):
    await message.answer(f"💬 Читайте отзывы наших клиентов: {REVIEWS_CHANNEL}")

# Полезные материалы
@router.message(F.text == "📚 Полезные материалы")
async def useful_materials(message: Message):
    text = """
📚 <b>Полезные материалы</b>

Выберите материал для скачивания:
    """
    await message.answer(text, reply_markup=kb.get_materials_menu())

@router.message(F.text.in_(["📘 3 ошибки селлера", "📗 Как выйти на маркетплейсы в 2025"]))
async def send_material(message: Message):
    contact_shared = await db.is_contact_shared(message.from_user.id)
    
    if not contact_shared:
        await message.answer("📱 Для получения материала поделитесь контактом:", 
                           reply_markup=kb.get_contact_keyboard())
    else:
        material_name = message.text
        await message.answer(f"📄 Отправляю материал: {material_name}")
        
        try:
            if "3 ошибки" in material_name:
                doc_path = get_file_path("guide1.pdf")
                document = FSInputFile(doc_path)
                await message.answer_document(document=document, caption="📘 3 ошибки селлера")
            else:
                doc_path = get_file_path("guide2.pdf")
                document = FSInputFile(doc_path)
                await message.answer_document(document=document, caption="📗 Как выйти на маркетплейсы в 2025")
        except FileNotFoundError:
            await message.answer("❌ Файл временно недоступен. Обратитесь к администратору.")

# FAQ
@router.message(F.text == "❓ FAQ")
async def faq(message: Message):
    text = """
❓ <b>Часто задаваемые вопросы</b>

<b>Q: Сколько времени занимает доставка?</b>
A: От 7 до 30 дней в зависимости от способа доставки.

<b>Q: Какие документы нужны для доставки?</b>
A: Инвойс, упаковочный лист, при необходимости - сертификаты.

<b>Q: Есть ли страхование груза?</b>
A: Да, мы предоставляем страхование на все виды доставки.

<b>Q: Как отследить груз?</b>
A: Вы получите трек-номер для отслеживания.
    """
    
    try:
        photo_path = get_file_path("faq.jpg")
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb.get_back_to_menu())
    except FileNotFoundError:
        await message.answer(text, reply_markup=kb.get_back_to_menu())

# Обработка контакта
@router.message(F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact: Contact = message.contact
    
    # Сохраняем контакт в базу данных
    await db.update_user_contact(message.from_user.id, contact.phone_number)
    
    # Отправляем контакт админу
    user_info = await db.get_user_info(message.from_user.id)
    contact_text = f"""
📱 <b>Новый контакт:</b>

👤 Имя: {contact.first_name} {contact.last_name or ''}
📞 Телефон: {contact.phone_number}
🆔 ID: {message.from_user.id}
👤 Username: @{message.from_user.username or 'не указан'}
    """
    
    try:
        await message.bot.send_message(ADMIN_ID, contact_text)
    except:
        pass
    
    # Проверяем состояние и завершаем процесс
    current_state = await state.get_state()
    
    if current_state == CalculationStates.waiting_contact:
        data = await state.get_data()
        await send_lead_to_admin(message.bot, message.from_user.id, "Расчёт доставки", **data)
        await db.add_lead(message.from_user.id, "Расчёт доставки", **data)
        await message.answer("✅ Ваш запрос на расчёт отправлен! Мы свяжемся с вами в ближайшее время.", 
                           reply_markup=kb.get_main_menu())
    elif current_state == ServiceStates.waiting_contact:
        await message.answer("✅ Спасибо! Ваш контакт сохранён.", reply_markup=kb.get_main_menu())
        await state.clear()
    else:
        await message.answer("✅ Спасибо! Ваш контакт сохранён.", reply_markup=kb.get_main_menu())
    
    await state.clear()

@router.callback_query(F.data == "company_card")
async def callback_company_card(callback: CallbackQuery):
    text = """
🏢 <b>Карточка организации</b>

<b>Реквизиты для оплаты:</b>

💳 <b>Расчётный счёт:</b> 40802810820000396550
🏦 <b>Название банка:</b> ООО "Банк Точка"
🔢 <b>БИК:</b> 044525104
📋 <b>Корреспондентский счёт:</b> 30101810745374525104
🆔 <b>ИНН:</b> 481308422231
📄 <b>Полное название:</b> ИП Казанцев Максим Олегович
    """
    
    try:
        photo_path = get_file_path("organ.jpg")
        photo = FSInputFile(photo_path)
        await callback.message.answer_photo(photo=photo, caption=text)
    except FileNotFoundError:
        await callback.message.answer(text)
    
    await callback.answer()

@router.callback_query(F.data == "social_networks")
async def callback_social_networks(callback: CallbackQuery):
    try:
        photo_path = get_file_path("socials.jpg")
        photo = FSInputFile(photo_path)
        await callback.message.answer_photo(photo=photo, caption="📱 <b>Выберите социальную сеть:</b>", reply_markup=kb.get_social_networks())
    except FileNotFoundError:
        await callback.message.answer("📱 <b>Выберите социальную сеть:</b>", reply_markup=kb.get_social_networks())
    await callback.answer()

# Курс валют
@router.message(F.text == "📈 Курс")
async def course_button(message: Message):
    await message.answer(f"💱 <b>Актуальный курс валют</b>\n\nПосмотреть курс: {COURSE_POST_LINK}")

@router.message(F.text == "📞 Получить услугу")
async def get_service(message: Message, state: FSMContext):
    # Проверяем, поделился ли пользователь контактом
    contact_shared = await db.is_contact_shared(message.from_user.id)
    
    if not contact_shared:
        await message.answer("📱 Для получения услуги поделитесь контактом:", reply_markup=kb.get_contact_keyboard())
        await state.set_state(ServiceStates.waiting_contact)
    else:
        await message.answer("📝 Как к вам обращаться?", reply_markup=kb.get_back_to_menu())
        await state.set_state(ServiceStates.waiting_name)

@router.callback_query(F.data.startswith("get_service_"))
async def callback_get_service(callback: CallbackQuery, state: FSMContext):
    service_name = callback.data.replace("get_service_", "").replace("_", " ")
    await state.update_data(service_type=service_name)
    
    # Проверяем, поделился ли пользователь контактом
    contact_shared = await db.is_contact_shared(callback.from_user.id)
    
    if not contact_shared:
        await callback.message.answer("📱 Для получения услуги поделитесь контактом:", reply_markup=kb.get_contact_keyboard())
        await state.set_state(ServiceStates.waiting_contact)
    else:
        await callback.message.answer("📝 Как к вам обращаться?", reply_markup=kb.get_back_to_menu())
        await state.set_state(ServiceStates.waiting_name)
    
    await callback.answer()

@router.message(StateFilter(ServiceStates.waiting_name))
async def process_service_name(message: Message, state: FSMContext):
    user_name = message.text
    data = await state.get_data()
    service_type = data.get('service_type', 'Не указана')
    
    # Отправляем заявку админу с указанием услуги
    service_text = f"""
🛠 <b>Новая заявка на услугу:</b>

🎯 <b>Услуга:</b> {service_type}
👤 <b>Имя:</b> {user_name}
🆔 <b>ID:</b> {message.from_user.id}
👤 <b>Username:</b> @{message.from_user.username or 'не указан'}
📞 <b>Телефон:</b> {await db.get_user_phone(message.from_user.id)}
    """
    
    try:
        await message.bot.send_message(ADMIN_ID, service_text)
    except:
        pass
    
    await message.answer("✅ Ваша заявка отправлена! Мы свяжемся с вами в ближайшее время.", 
                        reply_markup=kb.get_main_menu())
    await state.clear()

def get_file_path(filename):
    """Получает абсолютный путь к файлу в папке files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "files", filename)
