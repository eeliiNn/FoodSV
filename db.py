"""
db.py
Maneja la base de datos SQLite del proyecto: guarda cada detección
(alimento detectado, confianza, modelo usado, fecha) para poder
mostrar un historial en la app y sirve como evidencia para la
documentación del sistema.
"""

import sqlite3
from datetime import datetime

RUTA_DB = "foodsv.db"


def obtener_conexion():
    return sqlite3.connect(RUTA_DB)


def inicializar_db():
    """Crea la tabla de detecciones si no existe. Llamar una vez al iniciar la app."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detecciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            clase TEXT NOT NULL,
            confianza REAL NOT NULL,
            modelo TEXT NOT NULL,
            ruta_imagen TEXT
        )
    """)
    conexion.commit()
    conexion.close()


def guardar_deteccion(clase, confianza, modelo, ruta_imagen=None):
    """Guarda una detección individual en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO detecciones (fecha, clase, confianza, modelo, ruta_imagen) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), clase, confianza, modelo, ruta_imagen),
    )
    conexion.commit()
    conexion.close()


def guardar_detecciones_multiples(lista_detecciones, modelo, ruta_imagen=None):
    """lista_detecciones: lista de tuplas (clase, confianza)."""
    for clase, confianza in lista_detecciones:
        guardar_deteccion(clase, confianza, modelo, ruta_imagen)


def obtener_historial(limite=100):
    """Devuelve las últimas N detecciones, más recientes primero."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT fecha, clase, confianza, modelo, ruta_imagen FROM detecciones ORDER BY id DESC LIMIT ?",
        (limite,),
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def obtener_conteo_por_clase():
    """Para mostrar estadísticas: cuántas veces se detectó cada alimento."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT clase, COUNT(*) as total FROM detecciones GROUP BY clase ORDER BY total DESC"
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas
