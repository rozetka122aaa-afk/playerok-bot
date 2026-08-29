import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    WebAppInfo
)

TOKEN = "8810017490:AAHt_hI6667e2ikAjDJMLhDHvJwI8k30MlQ"

# Укажите точную ссылку на ваше Web App приложение (например, от Vercel, Render или Telegram)
WEB_APP_URL = "https://playerok.com" 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                # Для работы Mini App используется web_app=WebAppInfo(...)
                InlineKeyboardButton(
                    text="🔗 Открыть", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ],
            [
                InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
                InlineKeyboardButton(text="👛 Кошелек", callback_data="wallet")
            ],
            [
                InlineKeyboardButton(text="💬 Чаты", callback_data="chats"),
                InlineKeyboardButton(text="➕ Создать", callback_data="create")
            ],
            [
                InlineKeyboardButton(text="🎧 Поддержка", callback_data="support"),
                InlineKeyboardButton(text="🔗 Сайт", url="https://playerok.com")
            ]
        ]
    )
    return keyboard

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    caption_text = (
        "<b>🟢 Playerok — Сервис для проведения сделок</b>\n\n"
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
        logging.error(f"Ошибка при загрузке фото: {e}")
        await message.answer(
            text=caption_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    await callback.answer("Раздел находится в разработке", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
