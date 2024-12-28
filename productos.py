from db import connect_to_database

def obtener_listado_productos(connection, bot, chat_id):
    with connection.cursor() as cursor:
        # Realizamos la consulta para obtener los datos de los productos
        cursor.execute("SELECT producto, cantidad, precio, vendido, restantes, d_vendido FROM inventario")

        # Obtenemos todos los resultados de la consulta
        productos = cursor.fetchall()

        # Lista para almacenar los productos formateados
        listado = []

        # Procesamos cada producto y lo formateamos
        for producto in productos:
            producto_nombre = producto[0]
            cantidad = producto[1]
            precio = producto[2]
            vendido = producto[3]
            restante = producto[4]
            d_vendido = producto[5]

            # Formato solicitado
            formato_producto = f"{producto_nombre} Cantidad: {cantidad} - ${precio} | Se ha vendido: {vendido} | Quedan: {restante} | Total vendido: ${d_vendido}"
            listado.append(formato_producto)

        bot.send_message(chat_id, listado)

def agregar_producto(connection, producto, cantidad, precio, bot, chat_id):
    with connection.cursor() as cursor:
        # Calculamos el valor de 'restantes' y 'd_vendido'
        restantes = cantidad  # Inicialmente, la cantidad restante es igual a la cantidad
        d_vendido = 0  # Inicialmente, el total vendido es 0

        # Realizamos la consulta para insertar el nuevo producto
        query = """
        INSERT INTO inventario (producto, cantidad, precio)
        VALUES (%s, %s, %s);
        """
        try:
            # Ejecutamos la consulta
            cursor.execute(query, (producto, cantidad, precio))
            connection.commit()  # Confirmamos los cambios en la base de datos
            bot.send_message(chat_id, f"Producto '{producto}' agregado exitosamente.")
        except Exception as e:
            connection.rollback()  # Si hay un error, deshacemos los cambios
            bot.send_message(chat_id, e)

def eliminar_producto(connection, producto, bot, chat_id):
    with connection.cursor() as cursor:
        # Realizamos la consulta para eliminar el producto
        query = """
        DELETE FROM inventario WHERE producto = %s;
        """
        try:
            cursor.execute(query, (producto,))
            connection.commit()  # Confirmamos los cambios en la base de datos
            if cursor.rowcount > 0:
                res = f"Producto '{producto}' eliminado exitosamente."
                bot.send_message(chat_id, res)
            else:
                res = f"No se encontró el producto '{producto}' para eliminar."
                bot.send_message(chat_id, res)
        except Exception as e:
            connection.rollback()  # Si hay un error, deshacemos los cambios
            bot.send_message(chat_id, e)

def editar_precio_producto(connection, producto, nuevo_precio, bot, chat_id):
    with connection.cursor() as cursor:
        # Realizamos la consulta para actualizar el precio del producto
        query = """
        UPDATE inventario
        SET precio = %s
        WHERE producto = %s;
        """
        try:
            cursor.execute(query, (nuevo_precio, producto))
            connection.commit()  # Confirmamos los cambios en la base de datos
            if cursor.rowcount > 0:
                res = f"El precio del producto '{producto}' ha sido actualizado a {nuevo_precio}."
                bot.send_message(chat_id, res)
            else:
                res = f"No se encontró el producto '{producto}' para actualizar el precio."
                bot.send_message(chat_id, res)
        except Exception as e:
            connection.rollback()  # Si hay un error, deshacemos los cambios
            bot.send_message(chat_id, e)

def editar_cantidad_vendida(connection, producto, nueva_cantidad_vendida, chat_id, bot):
    with connection.cursor() as cursor:
        # Realizamos la consulta para actualizar la cantidad vendida del producto
        query = """
        UPDATE inventario
        SET vendido = %s
        WHERE producto = %s;
        """
        try:
            cursor.execute(query, (nueva_cantidad_vendida, producto))
            connection.commit()  # Confirmamos los cambios en la base de datos
            if cursor.rowcount > 0:
                res = f"La cantidad vendida del producto '{producto}' ha sido actualizada a {nueva_cantidad_vendida}."
                bot.send_message(chat_id, res)
            else:
                res = f"No se encontró el producto '{producto}' para actualizar la cantidad vendida."
                bot.send_message(chat_id, res)
        except Exception as e:
            connection.rollback()  # Si hay un error, deshacemos los cambios
            bot.send_message(chat_id, e)
