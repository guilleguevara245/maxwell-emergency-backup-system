"""
Maxwell Medic System - by Guillermo Guevara

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
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_tablas():
    """
    Crea las tablas del sistema si todavia no existen.

    El DNI es la clave primaria de pacientes, y el legajo la de medicos:
    son identificadores reales, no numeros generados por el sistema.

    "activo" implementa borrado logico: en vez de eliminar un registro
    de verdad, se marca como inactivo, para conservar el historial.

    "fecha_registro" guarda cuando se creo cada registro, con fines
    de auditoria basica.

    Los turnos NO llevan fecha ni hora: Maxwell es un sistema de
    respaldo que registra la SOLICITUD de turno (paciente, especialidad,
    medico especifico si se pidio, motivo y observaciones). La fecha y
    hora se asignan despues, en el sistema principal. Por eso
    "medico_legajo" es opcional: solo se completa si el paciente pidio
    un medico en particular.
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
            email TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
            email TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_dni TEXT NOT NULL,
            especialidad TEXT NOT NULL,
            medico_legajo TEXT,
            motivo TEXT NOT NULL,
            observaciones TEXT,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            exportado INTEGER NOT NULL DEFAULT 0,
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_dni) REFERENCES pacientes(dni),
            FOREIGN KEY (medico_legajo) REFERENCES medicos(legajo)
        )
    """)

    # Registro libre de "codigo de turno del sistema principal" + DNI,
    # para anotar que un paciente fue atendido y despues cargarlo
    # manualmente en el sistema principal. No se relaciona con la
    # tabla turnos: el codigo lo asigna el sistema principal, que
    # Maxwell no conoce.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS confirmaciones_atencion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_turno TEXT NOT NULL,
            paciente_dni TEXT NOT NULL,
            exportado INTEGER NOT NULL DEFAULT 0,
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_dni) REFERENCES pacientes(dni)
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos lista: tablas creadas (o ya existentes).")


if __name__ == "__main__":
    crear_tablas()
