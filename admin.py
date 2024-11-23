from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text
from main import dp, bot
from config import ADMINS
from states import AdminStates
from databace import post_text, post_file_id, save_user, check_user, user_post
from keyboards.default import admin_btn


@dp.message_handler(commands="admin", state="*")
async def post_command(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in ADMINS:
        await message.answer("<b>Assalomu aleykum\n\nSiz Adminsiz 👤</b>", reply_markup=admin_btn)
        await AdminStates.admin.set()
    else:
        await message.answer("<b>Haqiqiy admin emassiz!</b>")


@dp.message_handler(Text(equals="Kanalga Post Joylash 💾"), state=AdminStates.admin)
async def kanal_send(message: types.Message, state: FSMContext):
    await message.answer("Post joylash uchun video yoki rasm yuboring 📽", reply_markup=types.ReplyKeyboardRemove())
    checking_user = await check_user(message.from_user.id)
    if checking_user:
        await AdminStates.file_id.set()
    else:
        await save_user(message.from_user.id)
        await AdminStates.file_id.set()


@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO], state=AdminStates.file_id)
async def postfileid(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        await post_file_id(file_id, user_id)
        await message.answer("Rasm tanlandi, endi post uchun matn yuboring ✅")
    elif message.content_type == types.ContentType.VIDEO:
        file_id = message.video.file_id
        await post_file_id(file_id, user_id)
        await message.answer("Video tanlandi, endi post uchun matn yuboring ✅")
    else:
        await message.answer("Faqat rasm yoki video yuboring.")
        return

    await state.update_data(file_id=file_id)
    await AdminStates.post_text.set()


@dp.message_handler(state=AdminStates.post_text)
async def save_post_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    post_text_content = message.text
    await post_text(user_id, post_text_content)
    posts_data = await user_post(user_id)
    if not posts_data:
        await message.answer("Xato yuz berdi: Post ma'lumotlari topilmadi.")
        await state.finish()
        return
    file_id = posts_data[2]
    groups_chat_ids = ['@strike_test_group', '@strikecw',]

    if file_id:
        try:
            if file_id.startswith("Ag"):
                for i in groups_chat_ids:
                    await dp.bot.send_photo(chat_id=i, photo=file_id, caption=post_text_content,
                                            parse_mode=ParseMode.HTML)
            elif file_id.startswith("BAAD") or file_id.startswith("CAAD"):
                for i in groups_chat_ids:
                    await dp.bot.send_document(chat_id=i, document=file_id, caption=post_text_content,
                                               parse_mode=ParseMode.HTML)
            else:
                for i in groups_chat_ids:
                    await dp.bot.send_video(chat_id=i, video=file_id, caption=post_text_content,
                                            parse_mode=ParseMode.HTML)

            await message.answer(f"""
Post ushbu kanal va gruplaga yuborildi ✅

1. {groups_chat_ids[0]}
2. {groups_chat_ids[1]}
            """)
        except Exception as e:
            await message.answer(f"Xato yuz berdi: {e}")
    else:
        await message.answer("Media fayl topilmadi.")

    await state.finish()
