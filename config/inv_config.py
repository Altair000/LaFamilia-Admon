from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from config.bot_config import bot

def inicio(chat_id, message_id):
    # Crear el teclado inline
    markup = InlineKeyboardMarkup()

    # Agregar botones inline
    button1 = InlineKeyboardButton("Inventario", callback_data="inventario")
    button2 = InlineKeyboardButton("Historial", callback_data="historial")
    button3 = InlineKeyboardButton("ADMIN", callback_data="admin")

    # Añadir los botones al teclado
    markup.add(button1, button2)
    markup.add(button3)

    # Enviar el mensaje con el teclado inline
    bot.edit_message_text("Elige una opción: ", chat_id, message_id, reply_markup=markup)