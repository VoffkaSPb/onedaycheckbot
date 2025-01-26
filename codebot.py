import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения ID канала
channel_id = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот, который проверяет подписку на канал. Используйте /setchannel для установки канала.')

async def set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global channel_id
    if context.args:
        channel_id = context.args[0]  # Получаем имя канала из аргументов
        await update.message.reply_text(f'Канал установлен: {channel_id}')
    else:
        await update.message.reply_text('Пожалуйста, укажите имя канала (например, @ваш_канал).')

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global channel_id
    if channel_id is None:
        await update.message.reply_text('Канал не установлен. Используйте /setchannel для установки канала.')
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or "неизвестный пользователь"

    try:
        # Проверяем подписку на канал
        member = await context.bot.get_chat_member(channel_id, user_id)

        # Если пользователь не подписан или подписан меньше дня
        if member.status in ['left', 'kicked']:
            # Удаляем сообщение
            await context.bot.delete_message(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            # Отправляем уведомление
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Сообщение пользователя {username} удалено, так как он не подписан на канал."
            )
        elif member.joined_date and (datetime.now() - member.joined_date).days < 1:
            # Удаляем сообщение
            await context.bot.delete_message(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            # Отправляем уведомление
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text=f"Сообщение пользователя {username} удалено, так как он подписан меньше одного дня."
            )
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")

def main() -> None:
    # Вставьте токен вашего бота
    application = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setchannel", set_channel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_subscription))

    application.run_polling()

if __name__ == '__main__':
    main()