import nest_asyncio
import asyncio
import logging
import first_bot_functions
import db

#
nest_asyncio.apply()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Запуск процесса поллинга новых апдейтов
async def main():
    await db.create_table()
    await first_bot_functions.dp.start_polling(first_bot_functions.bot)

if __name__ == "__main__":
    asyncio.run(main())