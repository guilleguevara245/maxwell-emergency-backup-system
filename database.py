"""
Maxwell Medic System — by Guillermo Guevara

Modulo de conexion y creacion de la base de datos SQLite.
"""

import sqlite3

NOMBRE_BASE_DATOS = "maxwell_medic.db"


def obtener_conexion():
    """
    Abre y devuelve una conexion a la base de datos SQLite.
    Si el archivo .db no existe, SQLite lo crea automaticamente.
    """
    conexion = sqlite3.connect(NOMBRE_BASE_DATOS)
    conexion.execute("PRAGMA foreign_keys = ON")  # activa las relaciones entre tablas
    return conexion


def crear_tablas():
    """
    Crea las tablas del sistema si todavia no existen.
    Se ejecuta una sola vez al iniciar el programa.

    El DNI es la clave primaria de pacientes, y el legajo la de medicos:
    son identificadores reales, no numeros generados por el sistema.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            dni TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT NOT NULL,
            telefono_fijo TEXT,
            email TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicos (
            legajo TEXT PRIMARY KEY,
            dni TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            especialidad TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_dni TEXT NOT NULL,
            medico_legajo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            motivo TEXT NOT NULL,
            FOREIGN KEY (paciente_dni) REFERENCES pacientes(dni),
            FOREIGN KEY (medico_legajo) REFERENCES medicos(legajo)
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos lista: tablas creadas (o ya existentes).")


if __name__ == "__main__":
    # Esto permite probar el archivo solo, ejecutando: python database.py
    crear_tablas()
