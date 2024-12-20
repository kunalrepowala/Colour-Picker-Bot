import logging
import asyncio
import os  # Import os module to fetch environment variables
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from web_server import start_web_server  # Import the web server function
from script1 import start, admin, button_handler, show_statistics, handle_hex_code, send_hex_image, send_hex_document, handle_photo, error_handler  # Import updated handlers and functions from script1.py

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def print_zero_one() -> None:
    # This function will print "0-1" repeatedly every 1 second
    while True:
        print("0-1")
        await asyncio.sleep(1)  # Wait for 1 second before printing again

async def run_bot() -> None:
    # Get the bot token from environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Fetch the bot token from the environment

    if not bot_token:
        raise ValueError("No TELEGRAM_BOT_TOKEN environment variable found")  # Ensure the token is available
    
    app = ApplicationBuilder().token(bot_token).build()  # Use the bot token

   

    # script 2 handlers
    app.add_handler(CommandHandler("start", start))  # Add start handler again (if needed)
    app.add_handler(CommandHandler("admin", admin))  # Add admin handler
    app.add_handler(CallbackQueryHandler(button_handler))  # Add button callback handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hex_code))  # Handle text excluding commands
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Handle photo messages
    
    app.add_error_handler(error_handler)  # Error handler for the bot

    # Run the bot polling
    await app.run_polling()

async def main() -> None:
    # Run both the bot, the web server, and the print_zero_one function concurrently
    await asyncio.gather(run_bot(), start_web_server(), print_zero_one())

if __name__ == '__main__':
    asyncio.run(main())
