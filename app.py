from flask import Flask, render_template, request, redirect, jsonify
from db import obtener_conexion
from estructuras import lista_productos, cola_pedidos, pila_devoluciones, diccionario_productos

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# API REST para obtener productos desde SQL Server
@app.route("/api/productos", methods=["GET"])
def api_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, categoria, precio, stock FROM productos")
    filas = cursor.fetchall()

    productos = []

    for fila in filas:
        producto = {
            "id": fila[0],
            "nombre": fila[1],
            "categoria": fila[2],
            "precio": float(fila[3]),
            "stock": fila[4]
        }
        productos.append(producto)

    cursor.close()
    conexion.close()

    # Uso de lista
    lista_productos.clear()
    for producto in productos:
        lista_productos.append(producto)

    # Uso de diccionario
    diccionario_productos.clear()
    for producto in productos:
        diccionario_productos[producto["id"]] = producto

    return jsonify(lista_productos)


# Vista para mostrar productos
@app.route("/productos")
def productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, categoria, precio, stock FROM productos")
    filas = cursor.fetchall()

    productos = []

    for fila in filas:
        producto = {
            "id": fila[0],
            "nombre": fila[1],
            "categoria": fila[2],
            "precio": float(fila[3]),
            "stock": fila[4]
        }
        productos.append(producto)

    cursor.close()
    conexion.close()

    return render_template("productos.html", productos=productos)


# Agregar producto a SQL Server
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form["nombre"]
    categoria = request.form["categoria"]
    precio = request.form["precio"]
    stock = request.form["stock"]

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO productos (nombre, categoria, precio, stock)
    VALUES (?, ?, ?, ?)
    """

    cursor.execute(sql, (nombre, categoria, precio, stock))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect("/productos")


# Vista de pedidos usando cola
@app.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    if request.method == "POST":
        producto = request.form["producto"]
        cantidad = request.form["cantidad"]

        pedido = {
            "producto": producto,
            "cantidad": cantidad
        }

        # Uso de cola: el primero que entra es el primero que sale
        cola_pedidos.append(pedido)

        return redirect("/pedidos")

    return render_template("pedidos.html", pedidos=cola_pedidos)


# Atender el primer pedido de la cola
@app.route("/atender_pedido")
def atender_pedido():
    if len(cola_pedidos) > 0:
        cola_pedidos.pop(0)

    return redirect("/pedidos")


# Vista de devoluciones usando pila
@app.route("/devoluciones", methods=["GET", "POST"])
def devoluciones():
    if request.method == "POST":
        producto = request.form["producto"]
        motivo = request.form["motivo"]

        devolucion = {
            "producto": producto,
            "motivo": motivo
        }

        # Uso de pila: la última devolución registrada se revisa primero
        pila_devoluciones.append(devolucion)

        return redirect("/devoluciones")

    return render_template("devoluciones.html", devoluciones=pila_devoluciones)


# Revisar la última devolución de la pila
@app.route("/revisar_devolucion")
def revisar_devolucion():
    if len(pila_devoluciones) > 0:
        pila_devoluciones.pop()

    return redirect("/devoluciones")


# Ruta opcional para buscar un producto por ID usando diccionario
@app.route("/api/producto/<int:id_producto>", methods=["GET"])
def api_producto_por_id(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre, categoria, precio, stock FROM productos")
    filas = cursor.fetchall()

    diccionario_productos.clear()

    for fila in filas:
        producto = {
            "id": fila[0],
            "nombre": fila[1],
            "categoria": fila[2],
            "precio": float(fila[3]),
            "stock": fila[4]
        }

        diccionario_productos[producto["id"]] = producto

    cursor.close()
    conexion.close()

    producto_encontrado = diccionario_productos.get(id_producto)

    if producto_encontrado:
        return jsonify(producto_encontrado)
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)