# Módulos locales
from config.bot_config import bot, get_admin_ids
from config.db_config import conexion
from funciones.inventario import obtener_productos, crear_botones_inline, obtener_historial, generar_pdf, obtener_history
# Módulos de terceros
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Comando /start para iniciar el bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
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
    bot.send_message(message.chat.id, "Elige una opción:", reply_markup=markup)

# Manejo de las respuestas a los botones inline
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Comprobación de administradores
    administradores = [get_admin_ids()]  # Asegurarnos de que es una lista
    if call.data == "inventario":
        # Obtener los productos de la primera página
        productos = obtener_productos(pagina=1)
        # Crear los botones inline con la información de los productos
        markup = crear_botones_inline(productos, pagina=1)
        # Enviar el mensaje con los botones inline
        bot.edit_message_text("Selecciona un producto:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "historial":
        productos = obtener_history()

        # Formatea la respuesta
        mensaje = "Historial de productos:\n\n"
        for producto, cantidad, vendido, d_vendido, restantes in productos:
            mensaje += f"-{producto}: De una cantidad de {cantidad} se han vendido {vendido} dando un total de {d_vendido} pesos y quedando un restante de {restantes}.\n\n"

        # Crear los botones inline
        markup = InlineKeyboardMarkup()
        boton_resumen = InlineKeyboardButton("Resumen", callback_data="history_resumen")
        boton_volver = InlineKeyboardButton("Volver", callback_data="history_volver")
        boton_exportar = InlineKeyboardButton("Exportar", callback_data="history_exportar")
        markup.add(boton_resumen, boton_volver, boton_exportar)

        bot.send_message(call.message.chat.id, mensaje, reply_markup=markup)

    elif call.data == 'admin':
        if call.from_user.id not in administradores:
            bot.answer_callback_query(call.id, "No tienes acceso a esta funcionalidad.")
            bot.send_message(call.message.chat.id, "Lo siento, esta funcionalidad es solo para administradores.")
            return

        # Menú principal de administrador
        teclado_admin = InlineKeyboardMarkup(row_width=1)
        teclado_admin.add(
            InlineKeyboardButton("Agregar un producto", callback_data="product_agregar"),
            InlineKeyboardButton("Eliminar un producto", callback_data="product_eliminar"),
            InlineKeyboardButton("Cambiar precio", callback_data="product_precio")
            )
        bot.send_message(call.message.chat.id, "Bienvenido al panel de administración:", reply_markup=teclado_admin)

    # Manejador para las opciones de Historial (Resumen, Volver, Exportar)
    elif call.data.startswith("history_"):
        option = call.data.split("_")[1]  # Obtener la opción después de 'history_'

        if option == "resumen":
            productos = obtener_history()
            total = sum(d_vendido for _, _, _, d_vendido, _ in productos)

            # Enviar el total al usuario
            bot.answer_callback_query(call.id, "Resumen calculado.")
            bot.send_message(call.message.chat.id, f"El total de dinero es: {total} pesos.")

        elif option == "volver":
            from config.inv_config import inicio
            inicio(call.message.chat.id, call.message.message_id)  # Llamas a la función pasando el ID del chat

        elif option == "exportar":
            productos = obtener_historial()

            # Generar el PDF con los productos
            pdf_output = generar_pdf(productos)

            # Enviar el archivo PDF al usuario
            bot.answer_callback_query(call.id, "Exportando PDF...")
            with open(pdf_output, 'rb') as pdf_file:
                bot.send_document(call.message.chat.id, pdf_file)

    elif call.data.startswith("product_"):
        option = call.data.split("_")[1] if len(call.data.split("_")) > 1 else None

        if option == "agregar":
            msg = bot.send_message(call.message.chat.id, "Introduce el nombre del producto:")
            bot.register_next_step_handler(msg, obtener_nombre_producto)

        elif option == "eliminar":
            productos = obtener_productos()  # Función que recupera los productos de la base de datos
            if not productos:
                bot.send_message(call.message.chat.id, "No hay productos disponibles para eliminar.")
                return

            teclado_productos = InlineKeyboardMarkup(row_width=1)
            for producto in productos:
                producto = producto[0]
                teclado_productos.add(InlineKeyboardButton(producto, callback_data=f"eliminar_{producto}"))
            teclado_productos.row_width = 3
            botones = []
            pagina=1
            PRODUCTOS_POR_PAGINA=5
            if pagina > 1:
                botones.append(InlineKeyboardButton("◀️", callback_data=f"page_{pagina - 1}"))
            botones.append(InlineKeyboardButton("Inicio", callback_data="inicio"))
            if len(productos) == PRODUCTOS_POR_PAGINA:
                botones.append(InlineKeyboardButton("▶️", callback_data=f"page_{pagina + 1}"))
            teclado_productos.add(*botones)
            bot.send_message(call.message.chat.id, "Selecciona el producto a eliminar:", reply_markup=teclado_productos)

        elif option == "precio":
            productos = obtener_productos()  # Función que recupera los productos de la base de datos
            if not productos:
                bot.send_message(call.message.chat.id, "No hay productos disponibles para eliminar.")
                return

            teclado_productos = InlineKeyboardMarkup(row_width=1)
            for producto in productos:
                precio = f"${producto[2]}"
                producto = producto[0]
                teclado_productos.add(InlineKeyboardButton(f"{producto} | {precio}", callback_data=f"precio_{producto}"))
            teclado_productos.row_width = 3
            botones = []
            pagina = 1
            PRODUCTOS_POR_PAGINA = 5
            if pagina > 1:
                botones.append(InlineKeyboardButton("◀️", callback_data=f"pagination_{pagina - 1}"))
            botones.append(InlineKeyboardButton("Inicio", callback_data="inicio"))
            if len(productos) == PRODUCTOS_POR_PAGINA:
                botones.append(InlineKeyboardButton("▶️", callback_data=f"pagination_{pagina + 1}"))
            teclado_productos.add(*botones)
            bot.send_message(call.message.chat.id, "Selecciona el producto a cambiar el precio:", reply_markup=teclado_productos)

    elif call.data.startswith("precio_"):
        productos = obtener_productos()
        option = call.data.split("_")[1]
        for producto in productos:
            if option in producto:
                precio = producto[2]
                producto = producto[0]
                bot.send_message(call.message.chat.id, f"Precio actual del producto {producto} -> ${precio}")
                msg = bot.send_message(call.message.chat.id, "Diga el nuevo precio:")
                bot.register_next_step_handler(msg, confirmar_cambio_precio, producto, precio)

    elif call.data.startswith("eliminar_"):
        productos = obtener_productos()
        option = call.data.split("_")[1]
        for producto in productos:
            if option in producto:
                producto = producto[0]
                cursor = conexion.cursor()
                sql = "DELETE FROM inventario WHERE producto = %s"
                cursor.execute(sql, (producto,))
                conexion.commit()
                if cursor.rowcount > 0:
                    bot.send_message(call.message.chat.id, f"Producto {producto} eliminado satisfactoriamente.")

    elif call.data == "inicio":
        send_welcome(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data.startswith("page_"):
        # Obtener el número de página del callback_data
        pagina = int(call.data.split("_")[1])
        # Obtener los productos para la nueva página
        productos = obtener_productos(pagina)
        teclado_productos = InlineKeyboardMarkup(row_width=1)
        for producto in productos:
            producto = producto[0]
            teclado_productos.add(InlineKeyboardButton(producto, callback_data=f"eliminar_{producto}"))
        teclado_productos.row_width = 3
        botones = []
        pagina = pagina
        PRODUCTOS_POR_PAGINA = 5
        if pagina > 1:
            botones.append(InlineKeyboardButton("◀️", callback_data=f"page_{pagina - 1}"))
        botones.append(InlineKeyboardButton("Inicio", callback_data="inicio"))
        if len(productos) == PRODUCTOS_POR_PAGINA:
            botones.append(InlineKeyboardButton("▶️", callback_data=f"page_{pagina + 1}"))
        teclado_productos.add(*botones)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Página {pagina}:\nSelecciona el producto a eliminar:",
            reply_markup=teclado_productos
        )

    elif call.data.startswith("pagination_"):
        # Obtener el número de página del callback_data
        pagina = int(call.data.split("_")[1])
        # Obtener los productos para la nueva página
        productos = obtener_productos(pagina)
        teclado_productos = InlineKeyboardMarkup(row_width=1)
        for producto in productos:
            precio = producto[2]
            producto = producto[0]
            teclado_productos.add(InlineKeyboardButton(f"{producto} | ${precio}", callback_data=f"precio_{producto}"))
        teclado_productos.row_width = 3
        botones = []
        pagina = pagina
        PRODUCTOS_POR_PAGINA = 5
        if pagina > 1:
            botones.append(InlineKeyboardButton("◀️", callback_data=f"pagination_{pagina - 1}"))
        botones.append(InlineKeyboardButton("Inicio", callback_data="inicio"))
        if len(productos) == PRODUCTOS_POR_PAGINA:
            botones.append(InlineKeyboardButton("▶️", callback_data=f"pagination_{pagina + 1}"))
        teclado_productos.add(*botones)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Página {pagina}:\nSelecciona el producto a cambiar el precio:",
            reply_markup=teclado_productos
        )

def obtener_nombre_producto(message):
    nombre_producto = message.text.replace(" ", "").title()
    msg = bot.send_message(message.chat.id, f"Producto: {nombre_producto}. Ahora, introduce la cantidad inicial:")
    bot.register_next_step_handler(msg, obtener_cantidad, nombre_producto)

def obtener_cantidad(message, nombre_producto):
    cantidad = int(message.text)
    msg = bot.send_message(message.chat.id, f"Cantidad: {cantidad}. Ahora, introduce el precio:")
    bot.register_next_step_handler(msg, obtener_precio, nombre_producto, cantidad)

def obtener_precio(message, nombre_producto, cantidad):
    precio = int(message.text)
    # Aquí se guardaría el producto en la base de datos
    try:
        cursor = conexion.cursor()
        query = """
                INSERT INTO inventario (producto, cantidad, precio)
                VALUES (%s, %s, %s);
                """
        # Ejecutar la consulta con los valores proporcionados
        cursor.execute(query, (nombre_producto, cantidad, precio))
        conexion.commit()
        print("Producto agregado exitosamente.")
        bot.send_message(message.chat.id, f"Producto agregado exitosamente.")
    except Exception as e:
        conexion.rollback()
        print(f"Error al agregar el producto: {e}")
    finally:
        # Cerrar el cursor
        cursor.close()

@bot.message_handler(func=lambda msg: msg.text.isdigit() and int(msg.text) > 0)
def confirmar_cambio_precio(message, producto, precio):
    nuevo_precio = int(message.text)
    if nuevo_precio == precio:
        bot.send_message(message.chat.id, 'El nuevo precio no puede ser igual al precio actual. Intentelo de nuevo.')
        return
    # Aquí se actualizaría el precio en la base de datos
    cursor = conexion.cursor()
    sql = "UPDATE inventario SET precio = %s WHERE producto = %s"
    cursor.execute(sql, (nuevo_precio, producto))
    conexion.commit()
    if cursor.rowcount > 0:
        bot.send_message(message.chat.id, f"Precio del producto '{producto}' actualizado a ${nuevo_precio}.")
        cursor.close()

if __name__ == '__main__':
    print("Bot Iniciado")
    bot.infinity_polling()
