import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    WebAppInfo,
    FSInputFile
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ================= КОНФИГУРАЦИЯ =================
BOT_TOKEN = "8810017490:AAHt_hI6667e2ikAjDJMLhDHvJwI8k30MlQ"
ADMIN_ID = 2011272893
WEBAPP_URL = "https://playerok-webapp.vercel.app/"

SITE_URL = "https://playerok.com"    

users_db = set()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# ================= СОСТОЯНИЯ FSM =================
class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_account_update = State()
    waiting_for_broadcast = State()

# ================= КЛАВИАТУРЫ =================
def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Открыть", 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data="btn_profile"),
                InlineKeyboardButton(text="👛 Кошелек", callback_data="btn_wallet")
            ],
            [
                InlineKeyboardButton(text="💬 Чаты", callback_data="btn_chats"),
                InlineKeyboardButton(text="➕ Создать", callback_data="btn_create")
            ],
            [
                InlineKeyboardButton(text="🎧 Поддержка", callback_data="btn_support"),
                InlineKeyboardButton(text="🔗 Сайт ↗", url=SITE_URL)
            ]
        ]
    )

def get_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔔 Отправить уведомление об аккаунте", callback_data="admin_send_acc_update")
            ],
            [
                InlineKeyboardButton(text="📢 Общая рассылка", callback_data="admin_broadcast"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
            ]
        ]
    )

# ================= ХЕНДЛЕРЫ =================
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    users_db.add(message.from_user.id)
    
    caption_text = (
        "🟢 <b>Playerok — Сервис для проведения сделок</b>\n\n"
        "Покупайте, продавайте и обменивайте товары или услуги безопасно и удобно 🎄"
    )
    
    try:
        photo = FSInputFile("IMG_3387.jpeg")
        await message.answer_photo(
            photo=photo,
            caption=caption_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка при загрузке баннера: {e}")
        await message.answer(
            text=caption_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query(F.data.startswith("btn_"))
async def process_menu_buttons(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    
    responses = {
        "profile": "👤 <b>Ваш профиль в Playerok:</b>\n\nID: <code>{}</code>\nБаланс: 0.00 RUB",
        "wallet": "👛 <b>Кошелек Playerok</b>\n\nДоступный баланс: 0.00 RUB",
        "chats": "💬 <b>Мои чаты</b>\n\nУ вас пока нет активных диалогов.",
        "create": "➕ <b>Создание сделки</b>\n\nВыберите категорию товара или услуги.",
        "support": "🎧 <b>Поддержка Playerok</b>\n\nОбратитесь к оператору через форму в приложении."
    }
    
    text = responses.get(action, "Раздел обновляется.").format(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")

# ================= АДМИН-ПАНЕЛЬ (/admin) =================
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer(
        "⚙️ <b>Панель администратора Playerok</b>\n\nВыберите действие:",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )

@dp.callback_query(F.data == "admin_send_acc_update")
async def admin_acc_update_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
    await callback.message.answer("Введите **ID пользователя** для отправки уведомления:")
    await state.set_state(AdminStates.waiting_for_user_id)

@dp.message(AdminStates.waiting_for_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        target_id = int(message.text.strip())
        await state.update_data(target_user_id=target_id)
        await message.answer("Введите текст **уведомления об обновлении аккаунта**:")
        await state.set_state(AdminStates.waiting_for_account_update)
    except ValueError:
        await message.answer("❌ Введите корректный числовой ID.")

@dp.message(AdminStates.waiting_for_account_update)
async def process_acc_update_text(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    target_id = data.get("target_user_id")
    update_text = message.text

    notification_caption = (
        "🔔 <b>PLAYEROK: УВЕДОМЛЕНИЕ ОБ АККАУНТЕ</b>\n\n"
        f"{update_text}\n\n"
        "<i>Если это были не вы, обратитесь в поддержку.</i>"
    )

    try:
        photo = FSInputFile("IMG_3387.jpeg")
        await bot.send_photo(
            chat_id=target_id,
            photo=photo,
            caption=notification_caption,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        await message.answer(f"✅ Уведомление успешно отправлено пользователю <code>{target_id}</code>!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки пользователю <code>{target_id}</code>: {e}")
    
    await state.clear()

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
    await callback.message.answer(f"📊 Пользователей в базе: <b>{len(users_db)}</b>", parse_mode="HTML")

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.answer()
    await callback.message.answer("Введите текст рассылки:")
    await state.set_state(AdminStates.waiting_for_broadcast)

@dp.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text
    count = 0
    for user_id in users_db:
        try:
            await bot.send_message(user_id, text, parse_mode="HTML")
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"📢 Рассылка завершена. Успешно: <b>{count}</b>", parse_mode="HTML")
    await state.clear()

# ================= ЗАПУСК =================
async def main():
    try:
        await bot.set_my_name("Playerok")
    except Exception:
        pass
        
    print("Бот Playerok запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
