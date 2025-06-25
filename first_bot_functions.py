from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json
from pathlib import Path
import db


# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = 'YOUR_BOT_TOKEN'

# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()

# Структура квиза
path = Path('quiz_data.json')
quiz_data = json.loads(path.read_text(encoding='utf-8'))

def generate_options_keyboard(answer_options, right_answer):
  # Создаем сборщика клавиатур типа Inline
    builder = InlineKeyboardBuilder()

    # В цикле создаем 4 Inline кнопки, а точнее Callback-кнопки
    
    for option in answer_options:
        i = answer_options.index(option)
        builder.add(types.InlineKeyboardButton(
            # Текст на кнопках соответствует вариантам ответов
            text=option,
            # Присваиваем данные для колбэк запроса - индекс введенного ответа
            callback_data=str(i))
        )

    # Выводим по одной кнопке в столбик
    builder.adjust(1)
    return builder.as_markup()

async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    await db.update_quiz_index(user_id, current_question_index)

    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)


async def get_question(message, user_id):
    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await db.get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


#@dp.callback_query(F.data == "right_answer")

@dp.callback_query(F.data == "0")
@dp.callback_query(F.data == "1")
@dp.callback_query(F.data == "2")
@dp.callback_query(F.data == "3")
async def right_answer(callback: types.CallbackQuery):
    # редактируем текущее сообщение с целью убрать кнопки (reply_markup=None)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса для данного пользователя
    current_question_index = await db.get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    current_option = int(callback.data)

    #Выводим ответ пользователя    
    await callback.message.answer(f"Вы ответили: {quiz_data[current_question_index]['options'][current_option]}")
    
    if callback.data == str(quiz_data[current_question_index]['correct_option']):
        # Отправляем в чат сообщение, что ответ верный
        await callback.message.answer("Верно!")
    else:
        # Отправляем в чат сообщение об ошибке с указанием верного ответа
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    #Обновление статистики прохождения 
    await db.update_quiz_answer(callback.from_user.id, current_question_index, current_option, correct_option)
    
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await db.update_quiz_index(callback.from_user.id, current_question_index)
    
    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик кнопки начала игры и вывода статистики
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)

# Хэндлер на команду /stat
@dp.message(F.text=="Статистика")
@dp.message(Command("stat"))
async def cmd_stat(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте посмотрим статистику вашей игры")
    res = await db.get_quiz_stat(message.from_user.id)
    if res == -1:
        await message.answer(f"Вы ещё не ответили ни на один вопрос")
    else:
        await message.answer(f"Точность ваших ответов {res}%")


#path.write_text(json.dumps(quiz_data, indent=2), encoding='utf-8')
