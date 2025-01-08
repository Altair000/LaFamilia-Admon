from fpdf import FPDF
from config.db_config import conexion
from config.bot_config import bot
from config.inv_config import inicio
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Configuración de productos por página
PRODUCTOS_POR_PAGINA = 5

estado_global = {
    "producto_actual": None
}

mensajes_enviados = []

# Función para obtener los productos desde la base de datos
def obtener_productos(pagina=1, productos_por_pagina=PRODUCTOS_POR_PAGINA):
    try:
        cursor = conexion.cursor()
        offset = (pagina - 1) * productos_por_pagina
        query = """
        SELECT producto, cantidad, precio, vendido
        FROM inventario
        LIMIT %s OFFSET %s
        """
        cursor.execute(query, (productos_por_pagina, offset))
        productos = cursor.fetchall()
        cursor.close()
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []

# Función para crear los botones inline con la información de los productos
def crear_botones_inline(productos, pagina):
    markup = InlineKeyboardMarkup(row_width=1)
    for producto, cantidad, precio, vendidos in productos:
        texto = f"{producto}|Cantidad:{cantidad}|$:{precio}|Venta:{vendidos}"
        markup.add(InlineKeyboardButton(texto, callback_data=f"producto_{producto}"))

    # Botones de paginación
    markup.row_width = 3
    botones = []
    if pagina > 1:
        botones.append(InlineKeyboardButton("◀️", callback_data=f"pagina_{pagina - 1}"))
    botones.append(InlineKeyboardButton("Inicio", callback_data="inicio"))
    if len(productos) == PRODUCTOS_POR_PAGINA:
        botones.append(InlineKeyboardButton("▶️", callback_data=f"pagina_{pagina + 1}"))
    markup.add(*botones)
    return markup

# Manejador para el botón "Inicio"
@bot.callback_query_handler(func=lambda call: call.data == "inicio")
def manejar_inicio(call):
    inicio(chat_id=call.message.chat.id, message_id=call.message.message_id)

# Manejador para los botones de paginación
@bot.callback_query_handler(func=lambda call: call.data.startswith("pagina_"))
def manejar_paginacion(call):
    # Obtener el número de página del callback_data
    pagina = int(call.data.split("_")[1])

    # Obtener los productos para la nueva página
    productos = obtener_productos(pagina)

    # Crear nuevos botones inline
    markup = crear_botones_inline(productos, pagina)

    # Editar el mensaje existente para actualizar los botones
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Página {pagina}:\nSeleccione un producto:",
        reply_markup=markup
    )

# Manejador para los botones de productos
@bot.callback_query_handler(func=lambda call: call.data.startswith("producto_"))
def manejar_productos(call):
    cursor = conexion.cursor()
    producto = call.data.split("_")[1]
    estado_global["producto_actual"] = producto
    query = """
            SELECT producto, cantidad, precio, vendido, restantes, d_vendido
            FROM inventario
            WHERE producto = %s
            """
    # Ejecuta la consulta pasando el nombre del producto como parámetro
    cursor.execute(query, (producto,))
    producto = cursor.fetchone()
    texto = f'''
    Nombre: {producto[0]}
    Cantidad: {producto[1]}
    Precio: {producto[2]}
    Vendidos: {producto[3]}
    Restantes: {producto[4]}
    Importe: {producto[5]}
    '''

    markup = InlineKeyboardMarkup()
    agregar_button = InlineKeyboardButton("Agregar cantidad vendido", callback_data="detalle_agregar")
    restar_button = InlineKeyboardButton("Restar cantidad vendido", callback_data="detalle_restar")
    volver_button = InlineKeyboardButton("Volver", callback_data="detalle_volver")

    # Añadimos los botones al teclado
    markup.add(agregar_button, volver_button, restar_button)

    confirmacion = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=texto,
        reply_markup=markup
    )
    mensajes_enviados.append(confirmacion.message_id)

# Función para manejar los eventos de los botones
@bot.callback_query_handler(func=lambda call: call.data.startswith("detalle"))
def producto_query(call):
    data = call.data.split("_")[1]
    if data == "agregar":
        msg = bot.send_message(call.message.chat.id, "¿Cuántas unidades vendidas deseas agregar al producto?")
        bot.register_next_step_handler(msg, agregar_cantidad)

    elif data == "restar":
        msg = bot.send_message(call.message.chat.id, "¿Cuántas unidades vendidas deseas restar del producto?")
        bot.register_next_step_handler(msg, restar_cantidad)

    elif data == "volver":
        # Obtener los productos de la primera página
        productos = obtener_productos(pagina=1)
        # Crear los botones inline con la información de los productos
        markup = crear_botones_inline(productos, pagina=1)
        # Enviar el mensaje con los botones inline
        bot.edit_message_text("Selecciona un producto:", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

# Lógica para agregar cantidad vendida
def agregar_cantidad(message):
    try:
        cantidad = int(message.text)
        if cantidad <= 0:
            bot.send_message(message.chat.id, "La cantidad debe ser un número positivo.")
            return

        # Actualiza la base de datos, por ejemplo:
        query = "UPDATE inventario SET vendido = vendido + %s WHERE producto = %s"
        cursor = conexion.cursor()
        producto_actual = estado_global["producto_actual"]
        cursor.execute(query, (cantidad, producto_actual))

        bot.send_message(message.chat.id, f"Se han agregado {cantidad} unidades vendidas al producto {producto_actual}.")
        bot.edit_message_reply_markup(message.chat.id, mensajes_enviados, reply_markup=None)
        # Obtener los productos de la primera página
        productos = obtener_productos(pagina=1)
        # Crear los botones inline con la información de los productos
        markup = crear_botones_inline(productos, pagina=1)
        # Enviar el mensaje con los botones inline
        bot.send_message(message.chat.id, "Selecciona un producto:", reply_markup=markup)

        # Resetear producto actual después de la operación
        estado_global["producto_actual"] = None

    except ValueError:
        bot.send_message(message.chat.id, "Por favor, ingresa un número válido.")

# Lógica para restar cantidad vendida
def restar_cantidad(message):
    try:
        cantidad = int(message.text)
        if cantidad <= 0:
            bot.send_message(message.chat.id, "La cantidad debe ser un número positivo.")
            return

        # Actualiza la base de datos, por ejemplo:
        query = "UPDATE inventario SET vendido = vendido - %s WHERE producto = %s"
        cursor = conexion.cursor()
        producto_actual = estado_global["producto_actual"]
        cursor.execute(query, (cantidad, producto_actual))

        bot.send_message(message.chat.id, f"Se han restado {cantidad} unidades vendidas del producto {producto_actual}.")
        bot.edit_message_reply_markup(message.chat.id, mensajes_enviados, reply_markup=None)
        # Obtener los productos de la primera página
        productos = obtener_productos(pagina=1)
        # Crear los botones inline con la información de los productos
        markup = crear_botones_inline(productos, pagina=1)
        # Enviar el mensaje con los botones inline
        bot.send_message(message.chat.id, "Selecciona un producto:", reply_markup=markup)

        # Resetear producto actual después de la operación
        estado_global["producto_actual"] = None

    except ValueError:
        bot.send_message(message.chat.id, "Por favor, ingresa un número válido.")

# Función para obtener los productos de la base de datos
def obtener_historial():
    # Conéctate a tu base de datos
    cursor = conexion.cursor()

    # Ejecuta la consulta para obtener los productos
    query = """
        SELECT producto, cantidad, vendido, precio, d_vendido, restantes
        FROM inventario
    """
    cursor.execute(query)
    productos = cursor.fetchall()

    # Cierra la conexión
    cursor.close()

    return productos

def obtener_history():
    # Conéctate a tu base de datos
    cursor = conexion.cursor()

    # Ejecuta la consulta para obtener los productos
    query = """
        SELECT producto, cantidad, vendido, d_vendido, restantes
        FROM inventario
    """
    cursor.execute(query)
    productos = cursor.fetchall()

    # Cierra la conexión
    cursor.close()

    return productos

def generar_pdf(productos):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'config/DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    # Dibujar encabezado de la tabla
    pdf.set_fill_color(200, 220, 255)  # Color de fondo del encabezado
    pdf.cell(50, 10, "PRODUCTO", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "INICIO", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "VENDIDO", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "PRECIO", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "FINAL", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "IMPORTE", 1, 1, 'C', fill=True)

    total_d_vendido = 0  # Variable para acumular el total de d_vendido

    # Rellenar filas de la tabla
    for producto, cantidad, vendido, precio, d_vendido, restante in productos:
        pdf.cell(50, 10, producto, 1, 0, 'C')
        pdf.cell(30, 10, str(cantidad), 1, 0, 'C')
        pdf.cell(30, 10, str(vendido), 1, 0, 'C')
        pdf.cell(30, 10, str(precio), 1, 0, 'C')
        pdf.cell(30, 10, str(restante), 1, 0, 'C')
        pdf.cell(30, 10, f"${d_vendido}", 1, 1, 'C')
        total_d_vendido += d_vendido

    # Dejar un espacio antes de mostrar el total
    pdf.ln(5)

    # Mostrar el total al final de la tabla
    pdf.set_font('DejaVu', '', 14)  # Cambiar tamaño de fuente para el total
    pdf.cell(140, 10, "TOTAL:", 0, 0, 'R')  # Etiqueta alineada a la derecha
    pdf.cell(30, 10, f"${total_d_vendido}", 0, 1, 'C')  # Total alineado

    # Guardar el PDF en un archivo temporal
    pdf_output = "tmp/Resumen.pdf"
    pdf.output(pdf_output)

    return pdf_output
