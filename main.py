import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from tgBot.handlers.handlers import router
from tgBot.konec import run_task_send, schedule_daily_task
# from deploymentbot.middlewares.middlewares import AudioFileMiddleware, BotMessageTrackerMiddleware
from tgBot.middlewares import MessageHandlerMiddleware

# Initialize logging
logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('TOKEN')
# Initialize Bot and Dispatcher
bot = Bot(token = TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    # dp.message.middleware(MessageHandlerMiddleware())
    dp.update.middleware(MessageHandlerMiddleware())  # Update middleware
    # dp.update.middleware(BotMessageTrackerMiddleware(bot))
    asyncio.create_task(run_task_send("./", bot))
    asyncio.create_task(schedule_daily_task())
    
    # await asyncio.Event().wait()

    try:
        # Start polling
        await dp.start_polling(bot)
    finally:
        # Ensure the bot's session is closed on shutdown
        await bot.session.close()
        logging.info("Bot session closed.")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
