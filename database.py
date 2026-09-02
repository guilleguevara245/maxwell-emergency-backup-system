"""
Maxwell Emergency Backup System - by Guillermo Guevara

Modulo de conexion y creacion de la base de datos SQLite.
"""

import sqlite3

NOMBRE_BASE_DATOS = "maxwell_medic.db"

# Tiempo (en segundos) que espera SQLite antes de tirar "database is
# locked" si otro proceso esta escribiendo. Con esto alcanza para que,
# si alguien abre Maxwell dos veces por error en la misma PC, la
# segunda instancia simplemente espere en vez de romperse en el acto.
TIEMPO_ESPERA_BLOQUEO_SEGUNDOS = 10


class BaseDeDatosCorruptaError(Exception):
    """
    El archivo de base de datos existe pero no es una base SQLite
    valida (esta danado o corrupto), o no se pudo leer/escribir por
    un problema de permisos.
    """


class BaseDeDatosBloqueadaError(Exception):
    """
    No se pudo acceder a la base de datos porque otro proceso la tiene
    bloqueada (por ejemplo, otra instancia de Maxwell abierta al mismo
    tiempo) y el tiempo de espera se agoto.
    """


def obtener_conexion():
    """
    Abre y devuelve una conexion a la base de datos SQLite.
    Si el archivo .db no existe, SQLite lo crea automaticamente.

    Usa el modo de journal WAL (Write-Ahead Logging), que permite que
    varias conexiones lean y escriban con mucha menos friccion que el
    modo por defecto, y un tiempo de espera ante bloqueos para que una
    segunda instancia de Maxwell abierta por error no se rompa de
    inmediato, sino que espere unos segundos antes de fallar.

    Si el archivo esta corrupto o bloqueado mas alla del tiempo de
    espera, se traduce el error crudo de sqlite3 a una excepcion propia
    con un mensaje claro para mostrarle al usuario.
    """
    try:
        conexion = sqlite3.connect(NOMBRE_BASE_DATOS, timeout=TIEMPO_ESPERA_BLOQUEO_SEGUNDOS)
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("PRAGMA journal_mode = WAL")
        conexion.execute(f"PRAGMA busy_timeout = {TIEMPO_ESPERA_BLOQUEO_SEGUNDOS * 1000}")
        return conexion
    except sqlite3.DatabaseError as error:
        mensaje_original = str(error).lower()
        if "locked" in mensaje_original or "busy" in mensaje_original:
            raise BaseDeDatosBloqueadaError(
                "No se pudo acceder a la base de datos porque esta bloqueada. "
                "Es posible que haya otra instancia de Maxwell abierta al mismo "
                "tiempo; cerrala y volve a intentar."
            ) from error
        raise BaseDeDatosCorruptaError(
            f"El archivo '{NOMBRE_BASE_DATOS}' no se pudo abrir como base de datos "
            "SQLite valida (puede estar corrupto o danado). Si el problema persiste, "
            "renombra ese archivo para hacer una copia de respaldo y volve a abrir "
            "Maxwell: se va a crear una base de datos nueva y vacia."
        ) from error


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
    try:
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
        # tabla turnos ni exige que el paciente este en pacientes: puede
        # tratarse de alguien que el sistema principal ya conocia de antes.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS confirmaciones_atencion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_turno TEXT NOT NULL,
                paciente_dni TEXT NOT NULL,
                observaciones TEXT,
                exportado INTEGER NOT NULL DEFAULT 0,
                fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conexion.commit()
    except sqlite3.DatabaseError as error:
        raise BaseDeDatosCorruptaError(
            f"El archivo '{NOMBRE_BASE_DATOS}' existe pero no se pudieron crear/leer "
            "sus tablas (puede estar corrupto o danado). Si el problema persiste, "
            "renombra ese archivo para hacer una copia de respaldo y volve a abrir "
            "Maxwell: se va a crear una base de datos nueva y vacia."
        ) from error
    finally:
        conexion.close()
    print("Base de datos lista: tablas creadas (o ya existentes).")


if __name__ == "__main__":
    crear_tablas()
