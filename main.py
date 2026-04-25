import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from ai_assistant import get_ai_answer

from database import Database 

TOKEN = "8788551055:AAEhrz6t6nIFldK7Jj2e4q_ywlaleWhZuu4"


bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database("my_service.db")

class ZapisForm(StatesGroup):
    pib = State()        
    phone = State()      
    car = State()        
    issue = State()      
    confirm = State()    
    ai_question = State() 


def golovne_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🤖 Консультація")
    builder.button(text="📝 Записатися")
    builder.button(text="🔍 Перевірити запис") 
    builder.button(text="📍 Адреса")
    builder.adjust(2) 
    return builder.as_markup(resize_keyboard=True)


def menu_zapisy():
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Так, записатися")
    builder.button(text="⬅️ Повернутися до меню")
    builder.adjust(1) 
    return builder.as_markup(resize_keyboard=True)


def phone_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Надіслати номер", request_contact=True))
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)



@dp.message(CommandStart())
async def welcome(message: types.Message):
    
    db.dodati_id(message.from_user.id)    
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 🔧\nЯ твій помічник MykolaivDrive.",
        reply_markup=golovne_menu()
    )


@dp.message(F.text == "🤖 Консультація")
async def start_ai_consult(message: types.Message, state: FSMContext):
    await state.set_state(ZapisForm.ai_question)
    await message.answer(
        "🔧 Я — ваш віртуальний майстер MykolaivDrive.\n"
        "Опишіть вашу проблему одним повідомленням (наприклад: 'свистить ремінь' або 'погано гріє пічка'). Після відповіді ви повернетесь до меню:",
        reply_markup=types.ReplyKeyboardRemove() 
    )

# 2. Обробка питання та ПОВЕРНЕННЯ меню
@dp.message(ZapisForm.ai_question)
async def process_ai_question(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Повернутися до меню":
        await state.clear()
        return await message.answer("Повертаємось...", reply_markup=golovne_menu())

    waiting_msg = await message.answer("🔍 Аналізую проблему... Зачекайте хвилинку.")
    
    answer = await get_ai_answer(message.text)
    
    await waiting_msg.edit_text(answer)
    
    await state.clear()
    
    await message.answer("Чим я можу допомогти ще?", reply_markup=golovne_menu())



@dp.message(F.text.contains("Адреса"))
async def send_address(message: types.Message):
    address_text = (
        "📍 **Наша адреса у Миколаєві:**\n"
        "вул. Троїцька, 242\n\n"
        "⏰ **Графік роботи:**\n"
        "Пн-Сб: 09:00 - 18:00\n"
        "Нд: Вихідний\n\n"
        "🔗 [Відкрити у Google Maps](https://www.google.com/maps/place/%D0%90%D0%86%D0%A1+%D0%9C%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D1%97%D0%B2+%D1%82%D0%B0+%D0%A1%D0%A2%D0%9E+%D0%90%D0%86%D0%A1+%D0%9C%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D1%97%D0%B2/@46.9713299,32.0909288,781m/data=!3m2!1e3!4b1!4m6!3m5!1s0x40c5ca5c12f56b2b:0x5757593c301962ae!8m2!3d46.9713299!4d32.0909288!16s%2Fg%2F1vjdnkwt?entry=ttu&g_ep=EgoyMDI2MDMyNC4wIKXMDSoASAFQAw%3D%3D)"
    )
    await message.answer(address_text, parse_mode="Markdown")
    await message.answer("Бажаєте здійснити запис?", reply_markup=menu_zapisy())

@dp.message(F.text == "⬅️ Повернутися до меню")
async def back_to_main(message: types.Message):
    await message.answer("Ви повернулися в головне меню", reply_markup=golovne_menu())

@dp.message(F.text == "🔍 Перевірити запис")
async def check_my_booking(message: types.Message):
    booking = db.pereviriti_zapis(message.from_user.id)
    
    if booking:
        text = (
            f"✅ **Ваш актуальний запис:**\n\n"
            f"👤 ПІБ: {booking[0]}\n"
            f"🚗 Авто: {booking[1]}\n"
            f"🛠 Проблема: {booking[2]}"
        )
        builder = ReplyKeyboardBuilder()
        builder.button(text="✅ Так, я буду")
        builder.button(text="❌ Видалити запис")
        builder.adjust(2) 
        
        await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        builder = ReplyKeyboardBuilder()
        builder.button(text="📝 Записатися")
        builder.button(text="⬅️ Повернутися до меню")
        builder.adjust(1)
        await message.answer("Записів поки ще немає. Бажаєте записатися?", 
                             reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "✅ Так, я буду")
async def confirm_presence(message: types.Message):
    await message.answer("Дякуємо, що вибрали нас, чекатимемо! 🔧", reply_markup=golovne_menu())

@dp.message(F.text == "❌ Видалити запис")
async def delete_booking_handler(message: types.Message):
    db.vidaliti_zapis(message.from_user.id)
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Так, новий запис")
    builder.button(text="🏠 Ні, в меню")
    builder.adjust(2)
    
    await message.answer("Ваш запис було успішно видалено. Бажаєте здійснити новий запис?", 
                         reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "🏠 Ні, в меню")
async def back_after_del(message: types.Message):
    await message.answer("Головне меню:", reply_markup=golovne_menu())


@dp.message(F.text.in_({"📝 Записатися", "✅ Так, записатися", "✅ Так, новий запис"}))
async def start_zapis(message: types.Message, state: FSMContext):
    await state.set_state(ZapisForm.pib)
    await message.answer("Введіть ваше ПІБ (Прізвище, Ім'я, По батькові):", 
                         reply_markup=types.ReplyKeyboardRemove())

@dp.message(ZapisForm.pib)
async def process_pib(message: types.Message, state: FSMContext):
    await state.update_data(pib=message.text)
    await state.set_state(ZapisForm.phone)
    await message.answer("Натисніть кнопку нижче, щоб поділитися номером телефону:", 
                         reply_markup=phone_menu())

@dp.message(ZapisForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.set_state(ZapisForm.pib)
        return await message.answer("Введіть ПІБ заново:", reply_markup=types.ReplyKeyboardRemove())
    
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
        await state.set_state(ZapisForm.car)
        builder = ReplyKeyboardBuilder()
        builder.button(text="⬅️ Назад")
        await message.answer("Введіть марку, модель та рік випуску авто:", 
                             reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer("Будь ласка, скористайтеся кнопкою '📱 Надіслати номер'")

@dp.message(ZapisForm.car)
async def process_car(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.set_state(ZapisForm.phone)
        return await message.answer("Надішліть телефон ще раз:", reply_markup=phone_menu())
    
    await state.update_data(car=message.text)
    await state.set_state(ZapisForm.issue)
    await message.answer("Опишіть, що саме сталося з авто:")

@dp.message(ZapisForm.issue)
async def process_issue(message: types.Message, state: FSMContext):
    await state.update_data(issue=message.text)
    user_data = await state.get_data()
    
    summary = (
        f"📋 **Ваш запис:**\n\n"
        f"👤 ПІБ: {user_data['pib']}\n"
        f"📞 Тел: {user_data['phone']}\n"
        f"🚗 Авто: {user_data['car']}\n"
        f"🛠 Проблема: {user_data['issue']}\n\n"
        f"Все вірно?"
    )
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Все вірно, записати")
    builder.button(text="🔄 Змінити дані")
    builder.button(text="❌ Скасувати")
    builder.adjust(2)
    
    await state.set_state(ZapisForm.confirm)
    await message.answer(summary, parse_mode="Markdown", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(ZapisForm.confirm)
async def confirm_booking(message: types.Message, state: FSMContext):
    if message.text == "✅ Все вірно, записати":
        user_data = await state.get_data()
        db.onoviti_zapis(
            message.from_user.id, 
            user_data['pib'], 
            user_data['phone'], 
            user_data['car'], 
            user_data['issue']
        )
        await message.answer("✅ Ваш запис прийнято! Очікуйте на дзвінок.", reply_markup=golovne_menu())
        await state.clear()
    elif message.text == "🔄 Змінити дані":
        await state.set_state(ZapisForm.pib)
        await message.answer("Почнемо спочатку. Введіть ПІБ:", reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.clear()
        await message.answer("Запис скасовано.", reply_markup=golovne_menu())

@dp.message(ZapisForm.ai_question)
async def process_ai_question(message: types.Message, state: FSMContext):
    waiting_msg = await message.answer("🔍 Аналізую проблему... Зачекайте хвилинку.")  
    answer = await get_ai_answer(message.text) 
    await waiting_msg.edit_text(answer) 
    await state.clear()
    
async def start_program():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_program())