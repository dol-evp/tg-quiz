import aiosqlite

DB_NAME = 'first_bot.db'

async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_answers (user_id INTEGER, question_index INTEGER, answer_index INTEGER, right_answer INTEGER, PRIMARY KEY(user_id,question_index))''')
        # Сохраняем изменения
        await db.commit()


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


async def update_quiz_answer(user_id, index, answer1, right_answer1):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если запись с данным user_id и index уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_answers (user_id, question_index, answer_index, right_answer) VALUES (?, ?, ?, ?)', (user_id, index, answer1, right_answer1))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_stat(user_id):
    # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем число ответов для заданного пользователя
        async with db.execute('SELECT count(user_id) FROM quiz_answers WHERE user_id = (?)', (user_id, )) as cursor:
            # Проверяем результат
            results_cnt = await cursor.fetchone()
            if results_cnt[0] != 0:
                async with db.execute('SELECT count(user_id) FROM quiz_answers WHERE answer_index=right_answer AND user_id = (?)', (user_id, )) as cursor:
                    right_results_cnt = await cursor.fetchone()
                    res = right_results_cnt[0]/results_cnt[0]
                    return int(100*round(res,2))
            else:
                return -1


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0