from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes
from telegram.ext import filters
from PIL import Image
import io
import random
from collections import Counter
from datetime import datetime, timedelta

ADMIN_ID = 7464687297  # Replace with your actual admin ID

# Store user hex codes and statistics
user_hex_codes = {}
user_activity = {}
bot_message_count = 0
first_deployed = datetime.now()
bot_active = True  # Global variable to control bot activity

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_message_count
    bot_message_count += 1

    keyboard = [
        [
            InlineKeyboardButton("ʜᴇx ᴄᴏᴅᴇs 🧭", url='https://www.google.com/search?q=colour+picker'),
            InlineKeyboardButton("Tᴜᴛᴏʀɪᴀʟ🐣", callback_data='tutorial')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "<b>🎨 Welcome to the Color Picker Bot!</b>\n\n"
        "🔍 <b>Send me a Hex Code</b> to get a high-quality image of that color.\n\n"
        "✨ <b>Hex Code Example:</b> <code>#3e344f</code>"
    )

    video_id = 'BAACAgUAAxkBAAMBZ2U-ktAmneR1WRnSO4EIz9jeHWgAAiUUAALtlsFXwAfXuPPUxWs2BA'
    await context.bot.send_video(
        chat_id=update.message.chat_id,
        video=video_id,
        caption=message,
        parse_mode='HTML',
        reply_markup=reply_markup,
        reply_to_message_id=update.message.message_id
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    state = "ON✳️" if bot_active else "OFF📴"
    keyboard = [
        [
            InlineKeyboardButton("Statistics 🇮🇲", callback_data='statistics'),
            InlineKeyboardButton("Mailing 📬", callback_data='mailing')
        ],
        [
            InlineKeyboardButton("Add Force Join ✳️", callback_data='force_join'),
            InlineKeyboardButton(state, callback_data='toggle_bot')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin Options:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    global bot_active
    if query.data == 'tutorial':
        await query.message.reply_text("𝗕𝗼𝘁 𝗙𝗲𝗮𝘁𝗿𝗲𝘀:\n\n𝗛𝗲𝘅 𝗖𝗼𝗱𝗲 𝗖𝗼𝗹𝗼𝘂𝗿: Send any HEX code like (#FF5733), and the bot will generate an HD image of that color.\n\n𝗥𝗮𝗻𝗱𝗼𝗺 𝗖𝗼𝗹𝗼𝗿: Tap the 'Random Colour' button to get a randomly generated color and its corresponding HEX code.\n\n𝗣𝗵𝗼𝘁𝗼 𝗖𝗼𝗹𝗼𝗿 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗶𝗼𝗻: Send a photo, and the bot will detect the most common colors in the image. However, if there are too many colors, the bot might get confused and the accuracy could decrease. Try to send images with fewer dominant colors for better results!\n\n\nYou can also access additional options through the 'Tutorial' and 'Get All' buttons to explore more features.", reply_to_message_id=query.message.message_id)
    elif query.data == 'get_all':
        user_id = query.from_user.id
        hex_codes = user_hex_codes.get(user_id, [])
        if hex_codes:
            for hex_code in hex_codes:
                await send_hex_image(query.message.chat_id, hex_code, context, query.message)
                await send_hex_document(query.message.chat_id, hex_code, context, query.message)
            await query.message.reply_text("All detected hex color photos and documents sent.", reply_to_message_id=query.message.message_id)
        else:
            await query.message.reply_text("No data found for hex codes.", reply_to_message_id=query.message.message_id)
    elif query.data == 'random_color':
        random_hex = f'#{random.randint(0, 0xFFFFFF):06x}'
        await send_hex_image(query.message.chat_id, random_hex, context, query.message)
        await send_hex_document(query.message.chat_id, random_hex, context, query.message)
    elif query.data == 'admin':
        await admin(update, context)
    elif query.data == 'toggle_bot':
        bot_active = not bot_active
        state = "ON✳️" if bot_active else "OFF📴"
        
        keyboard = [
            [
                InlineKeyboardButton("Statistics 🇮🇲", callback_data='statistics'),
                InlineKeyboardButton("Mailing 📬", callback_data='mailing')
            ],
            [
                InlineKeyboardButton("Add Force Join ✳️", callback_data='force_join'),
                InlineKeyboardButton(state, callback_data='toggle_bot')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_reply_markup(reply_markup=reply_markup)
        await query.message.reply_text(f"Bot is now {state}.", reply_to_message_id=query.message.message_id)
    elif query.data == 'statistics':
        await show_statistics(update, context)

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    total_users = len(user_activity)
    now = datetime.now()
    last_24_hours = sum(1 for time in user_activity.values() if now - time <= timedelta(hours=24))
    last_week = sum(1 for time in user_activity.values() if now - time <= timedelta(weeks=1))
    last_month = sum(1 for time in user_activity.values() if now - time <= timedelta(weeks=4))

    global bot_message_count
    statistics_message = (
        f"📊 <b>Bot Statistics</b>\n"
        f"👤 Total Users: {total_users}\n"
        f"🕒 Users in Last 24 Hours: {last_24_hours}\n"
        f"🕒 Users in Last Week: {last_week}\n"
        f"🕒 Users in Last Month: {last_month}\n"
        f"✉️ Total Messages Sent by Bot: {bot_message_count}\n"
        f"🕒 First Deployed: {first_deployed.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await query.message.reply_text(statistics_message, parse_mode='HTML')

async def handle_hex_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_message_count
    user_id = update.message.from_user.id
    user_activity[user_id] = datetime.now()  # Update timestamp for activity

    if not bot_active:
        return  # Do nothing if bot is inactive

    hex_code = update.message.text.strip()
    
    if not (len(hex_code) == 7 and hex_code.startswith('#')):
        bot_message_count += 1  # Count bot message
        video_id = 'BAACAgUAAxkBAAMCZ2U-kn3CpckrBAr_PBMrBFl0mnQAAiYUAALtlsFXonPrQUA8to02BA'
        caption_message = (
            "🚫 Invalid HEX Code\n\n"
            "Send a single valid Hex Code.\n"
            "Example: <code>#3e344f</code>."
        )
        keyboard = [
            [InlineKeyboardButton("Random Colour 🎨", callback_data='random_color')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_video(
            chat_id=update.message.chat_id,
            video=video_id,
            caption=caption_message,
            parse_mode='HTML',
            reply_markup=reply_markup,
            reply_to_message_id=update.message.message_id
        )
        return

    user_hex_codes[user_id] = [hex_code]  # Clear previous hex codes on new input
    
    await send_hex_image(update.message.chat_id, hex_code, context, update.message)
    await send_hex_document(update.message.chat_id, hex_code, context, update.message)

async def send_hex_image(chat_id, hex_code, context, reply_to_message=None):
    global bot_message_count
    image = Image.new("RGB", (100, 100), hex_code)
    byte_io = io.BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)

    await context.bot.send_photo(
        chat_id, 
        photo=InputFile(byte_io, filename='color.png'), 
        reply_to_message_id=reply_to_message.message_id if reply_to_message else None
    )
    bot_message_count += 1  # Count bot message

async def send_hex_document(chat_id, hex_code, context, reply_to_message=None):
    global bot_message_count
    image = Image.new("RGB", (100, 100), hex_code)
    byte_io = io.BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)

    await context.bot.send_document(
        chat_id, 
        document=InputFile(byte_io, filename=f'{hex_code}.png'), 
        reply_to_message_id=reply_to_message.message_id if reply_to_message else None
    )
    bot_message_count += 1  # Count bot message

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_message_count
    user_id = update.message.from_user.id
    user_activity[user_id] = datetime.now()  # Update timestamp for activity

    if not bot_active:
        return  # Do nothing if bot is inactive

    photo_file = update.message.photo[-1]
    file = await photo_file.get_file()
    byte_array = await file.download_as_bytearray()

    byte_io = io.BytesIO(byte_array)
    image = Image.open(byte_io).convert('RGB')
    colors = image.getdata()

    color_count = Counter(colors)
    most_common_colors = color_count.most_common(5)

    hex_colors = [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b), _ in most_common_colors]

    user_hex_codes[user_id] = hex_colors  # Store only the new colors

    numbered_hex_colors = "\n".join([f"<code>{hex_color}</code>" for hex_color in hex_colors])

    keyboard = [
        [
            InlineKeyboardButton("Get All ⚕️", callback_data='get_all')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Detected colors:\n<pre>{numbered_hex_colors}</pre>\n\nOptions:",
        reply_markup=reply_markup,
        parse_mode='HTML',
        reply_to_message_id=update.message.message_id
    )
    bot_message_count += 1  # Count bot message

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')
