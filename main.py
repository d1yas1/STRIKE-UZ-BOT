import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_polling
from datetime import datetime
from stats import periodic_statistics
import requests
from bs4 import BeautifulSoup
from databace import *
from config import BOT_TOKEN, GROUP_IDS
from keyboards.inline import language_buttons
from states import UserStates


# Bot sozlamalari
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


# Yangi a'zo uchun xush kelibsiz xabari
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_new_member(message: types.Message):
    for new_member in message.new_chat_members:
        username = new_member.username if new_member.username else new_member.full_name
        welcome_text = f"""
🇺🇿 Assalomu alaykum @{username}! 👋 Strike.Uz ga hush kelibsiz.
🌐 Mavjud serverlar ro’yxati uchun /server deb yozing.
✍️ Biz bilan bog’lanish: @MccallStrike

🇷🇺 Приветствуем тебя @{username}! Добро пожаловать в Strike.Uz. 👋
🌐 Список доступных серверов: /server
✍️ Связаться с нами: @MccallStrike
        """
        await message.answer(welcome_text)


# Start komanda
@dp.message_handler(commands='start', state="*")
async def cmd_start(message: types.Message):
    await message.answer("Iltimos tilni tanlang: 🇺🇿 O’zbek / 🇷🇺 Русский", reply_markup=language_buttons)
    checking_user = await check_user(message.from_user.id)
    if checking_user:
        await UserStates.language.set()
    else:
        await save_user(message.from_user.id)
        await UserStates.language.set()


# Til tanlash uchun handler
@dp.callback_query_handler(text="uzbek", state=UserStates.language)
async def uzbek_language(call: types.CallbackQuery, state):
    text = """<b>
Counter-Strike 1.6 ni online o’ynashni o’rganmoqchi bo’lsangiz /startcs - tugmasini bosing
/info - Strike.Uz proekti haqida ma'lumot
/server - Serverlar ro'yxati
/vip - Vip haqida ma'lumot
Qo’shimcha ma’lumotlar uchun: @MccallStrike
Bizni telegram kanalimizga obuna bo’ling: @STRIKEUZCHANNEL
Bizni Telegram guruhlarimizda faol bo’ling: @STRIKEUZCOMMUNITY @STRIKECW
@STRIKEUZREPORTS
    </b>"""
    await call.message.delete()
    await call.message.answer(text)
    await state.finish()


@dp.callback_query_handler(text="russian", state=UserStates.language)
async def russian_language(call: types.CallbackQuery, state):
    text = """<b>
Если хотите научиться играть в Counter-Strike 1.6 онлайн, нажмите кнопку /startcs.
/info - Информация о проекте Strike.Uz
/server - Список серверов
/vip - Информация о VIP
Для дополнительной информации: @MccallStrike
Подпишитесь на наш Telegram-канал: @STRIKEUZCHANNEL
Будьте активны в наших Telegram-группах: @STRIKEUZCOMMUNITY @STRIKECW @STRIKEUZREPORTS
    </b>"""
    await call.message.delete()
    await call.message.answer(text)
    await state.finish()


@dp.message_handler(commands="startcs")
async def cmd_start(message: types.Message):
    try:
        await message.answer_video(video="BAACAgIAAxkDAAIdUGc12VT1cdO5ijAmgoN_WJRWStcgAAKEVQAC-5GwSaSw3emPQ4z1NgQ")
    except:
        await message.answer_video(video=open("uploads/strike.mp4", "rb"))


@dp.message_handler(commands=['info'])
async def infoo(message: types.Message):
    await message.answer("""
<b>🇺🇿Strike.Uz ga hush kelibsiz! 👋</b>

<b>Strike.Uz</b> - bu O'zbekistondagi eng sifatli va qiziqarli Counter-Strike 1.6 serverlari. Agar siz eng kuchli o'yinchilari orasida hamda qiziqarli serverlarda o'ynashni xohlasangiz, unda hoziroq o'yinni Strike.Uz saytidan yuklab olishingizni so'raymiz!
O'yinni yuklab olish uchun Strike.uz saytimizga tashrif buyuring va <b>GS Client</b> tugmasini bosing. Serverning IP adreslarini /server buyrug'ini yozib yoki Strike.Uz saytimizdan topishingiz mumkin! <b> Biz sizni kutib qolamiz </b> 🔥

<b>🇷🇺Добро пожаловать в Strike.Uz! 👋</b>

<b>Strike.Uz</b> - это качественные и инетересные сервера Counter-Strike 1.6 в Узбекистане.Хотите поиграть с лучшими игроками страны, в интересных серверах то сейчас же скачивайте игру и присоеденяйтесь к нам!
Скачать игру вы можете на нашем сайте Strike.uz нажав на кнопку <b> GS Client.</b> ИП Адреса сервера вы можете получить прописав команду /server либо на нашем сайте Strike.Uz! <b> Мы ждем тебя 🔥 </b>
""")


@dp.message_handler(commands=['vip'])
async def vipp(message: types.Message):
    await message.answer("""<b>
🇺🇿Vip haqida batafsil ma'lumotlarni @MccallStrike dan olishingiz mumkin

🇷🇺Полную информацию про ВИП вы можете получить у @MccallStrike
</b>""")


# Serverlar ro'yxati
@dp.message_handler(commands=['server'])
async def server_list(message: types.Message):
    url = 'http://strike.uz'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    elements = soup.find_all('td')
    data = [element.text.strip() for element in elements]
    filtered_data = [d for d in data if isinstance(d, str)]

    total_online = 0
    total_capacity = 0
    server_details = ''

    for count, i in enumerate(filtered_data):
        if 'Strike.Uz' in i or 'YouTube' in i:
            server_name = filtered_data[count]
            ip_address = filtered_data[count + 3]
            map_name = filtered_data[count + 2]
            players_data = filtered_data[count + 1]
            current_players, max_capacity = map(int, players_data.split(' из '))
            percentage = (current_players / max_capacity) * 100
            total_online += current_players
            total_capacity += max_capacity
            server_details += f"""
<b>⚡️Server:</b> {server_name}
<b>🌐IP:</b> <code>{ip_address}</code>
<b>📍Map:</b> {map_name}
<b>👥Players:</b> {current_players} из {max_capacity} [{percentage:.0f}%]\n
"""

    overall_percentage = (total_online / total_capacity) * 100 if total_capacity > 0 else 0
    text = f"📊 <b>Statistics:</b> {total_online}/{total_capacity} [{overall_percentage:.1f}%]\n\n" + server_details
    await message.reply(text, parse_mode="HTML")


if __name__ == "__main__":
    from admin import dp,bot
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_statistics(bot))
    start_polling(dp, skip_updates=True)
