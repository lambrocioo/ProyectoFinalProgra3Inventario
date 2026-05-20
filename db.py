import pyodbc

def obtener_conexion():
    conexion = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=(localdb)\\MSSQLLocalDB;"
        "DATABASE=inventario_db;"
        "Trusted_Connection=yes;"
    )
    return conexion