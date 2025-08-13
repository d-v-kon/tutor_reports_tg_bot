import logging
from database import send_new_record, get_last_lesson, add_teacher

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! \n"
        f"Отправь мне \"/registration (Твои имя и фамилия)\" без кавычек и скобочек для дальнейшей работы \n"
        f"Например, /registration Василий Петечкин \n")


async def registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        _, teacher_name, teacher_surname = update.message.text.split()
    except ValueError:
        await update.message.reply_html(
            f"Ты ошибся с форматом сообщения! Попробуй снова")
        return
    teacher_full_name = f"{teacher_name} {teacher_surname}"
    teacher_telegram_id = user.id
    add_teacher(teacher_full_name, teacher_telegram_id)
    await update.message.reply_html(
        f"Теперь я знаю тебя, {teacher_full_name}! \n"
        f"Теперь отправляй мне информацию о своих уроках строго в таком формате:\n"
        f"День.Месяц.Год урока\n"
        f"Тип урока\n"
        f"Имя ученика\n"
        f"\n"
        f"Например:\n"
        f"02.12.2023\n"
        f"Індивідуальні, математика, 6 клас\n"
        f"Анастасія")


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    new_data = update.message.text
    teacher_id = update.effective_user.id
    send_new_record(new_data, teacher_id)
    await update.message.reply_text(f"Урок записан: \n {get_last_lesson(teacher_id)}")


def main():
    application = Application.builder().token("6649693798:AAEHiQTKv-BPOCGk1WRa5eqrgAr1eXzyLRk").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("registration", registration))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
