import logging
from dotenv import load_dotenv
import os

import pandas as pd
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
FILTER_CITY, FILTER_SITE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command,
    sending a welcome message along with the user's chat ID.
    """
    chat_id = update.message.chat_id
    await update.message.reply_text(
        f"🙏Ласкаво просимо!"
        "Використовуйте /filter_by_city для сортування резюме за сайтом.\n"
        "Використовуйте /filter_by_site для сортування резюме за містами."
    )


def format_resume(row):
    """
    Formats a single resume row into a readable string.
    """
    return (
        f"Робота: {row['job']}\n"
        f"Ім'я: {row['name']}\n"
        f"Досвід роботи: {row['years']}\n"
        f"Міста: {row['cities']}\n"
        f"Очікувана арплата: {row['salary']}\n"
        f"Інформація: {row['info']}\n"
        f"Сайт: {row['site']}\n"
        f"Актуальність: {row['relevance']}\n"
        "-------------------------"
    )


async def send_resumes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    filter_by: str = None,
    filter_value: str = None,
) -> None:
    """
    Sends resumes filtered by a specified field and value.
    """
    try:
        df = pd.read_csv("result_df.csv")
        if filter_by and filter_value:
            df = df[df[filter_by].str.contains(filter_value, case=False, na=False)]
        top_5_rows = df.head()
        message = "\n\n".join([format_resume(row) for _, row in top_5_rows.iterrows()])
        await update.message.reply_text(f"<pre>{message}</pre>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Помилка під час надсилання резюме: {e}")
        await update.message.reply_text("Сталася помилка під час надсилання резюме.")


async def filter_by_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the conversation for filtering by city.
    """
    await update.message.reply_text("Введіть назву міста для фільтрації:")
    return FILTER_CITY


async def filter_by_site(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Starts the conversation for filtering by site.
    """
    await update.message.reply_text("Введіть назву сайту для фільтрації:")
    return FILTER_SITE


async def city_filter_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user input for city filter.
    """
    city = update.message.text
    await send_resumes(update, context, filter_by="cities", filter_value=city)
    return ConversationHandler.END


async def site_filter_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user input for site filter.
    """
    site = update.message.text
    await send_resumes(update, context, filter_by="site", filter_value=site)
    return ConversationHandler.END


def main() -> None:
    """
    Sets up the Telegram bot application and
    starts polling for updates. Also, initializes
    the async scheduler.
    """
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    filter_city_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("filter_by_city", filter_by_city)],
        states={
            FILTER_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, city_filter_input)
            ],
        },
        fallbacks=[],
    )

    filter_site_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("filter_by_site", filter_by_site)],
        states={
            FILTER_SITE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, site_filter_input)
            ],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(filter_city_conv_handler)
    app.add_handler(filter_site_conv_handler)

    app.run_polling()


if __name__ == "__main__":
    load_dotenv()
    TG_BOT_TOKEN = os.getenv("TG_TOKEN")
    main()
