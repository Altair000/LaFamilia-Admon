from db import connect_to_database

def verificar_si_es_admin(connection, chat_id, bot, user_id):
    with connection.cursor() as cursor:
        # Realizamos la consulta para verificar si el ID existe y si es admin
        cursor.execute("SELECT admin FROM id WHERE id = %s", (user_id,))
        result = cursor.fetchone()  # Obtiene una fila (tupla)

        # Si el ID no existe, retornamos False (o también podrías lanzar una excepción)
        if result is None:
            return False

        # Verificamos si el usuario es admin
        admin = result[0]
        if admin:
            bot.send_message(chat_id, "Use '/admin_help' para ver los comandos de administración.")
        else:
            bot.send_message(chat_id, "Use '/help' para ver los comandos.")
