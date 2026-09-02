"""
Maxwell Emergency Backup System - by Guillermo Guevara

Tests automaticos del modulo database: deteccion de un archivo de
base de datos corrupto y tolerancia a escrituras concurrentes desde
mas de una conexion (por ejemplo, dos instancias de Maxwell abiertas
al mismo tiempo por error).
"""

import os
import sqlite3
import threading
import time
import unittest

import database
from database import (
    crear_tablas,
    obtener_conexion,
    conexion_segura,
    BaseDeDatosCorruptaError,
    BaseDeDatosBloqueadaError,
)


class TestBaseDeDatos(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic_db_errores.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)

    def tearDown(self):
        for extension in ("", "-wal", "-shm"):
            ruta = database.NOMBRE_BASE_DATOS + extension
            if os.path.exists(ruta):
                os.remove(ruta)

    def test_detecta_archivo_corrupto_como_error_claro(self):
        with open(database.NOMBRE_BASE_DATOS, "w") as archivo:
            archivo.write("esto no es una base de datos SQLite valida")

        with self.assertRaises(BaseDeDatosCorruptaError):
            crear_tablas()

    def test_tolera_escrituras_concurrentes_de_dos_instancias(self):
        crear_tablas()
        errores = []

        def escribir(indice):
            try:
                conexion = obtener_conexion()
                conexion.execute("BEGIN IMMEDIATE")
                time.sleep(0.3)
                conexion.execute(
                    """
                    INSERT INTO medicos (legajo, dni, nombre, apellido, especialidad, telefono, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (f"LEG{indice}", f"{indice}0000000", "Test", "Test", "Clinica", "111", "a@a.com"),
                )
                conexion.commit()
                conexion.close()
            except Exception as error:
                errores.append(error)

        hilos = [threading.Thread(target=escribir, args=(i,)) for i in range(3)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        self.assertEqual(errores, [], "No deberian ocurrir errores de bloqueo con dos escrituras simultaneas")

        conexion = obtener_conexion()
        cantidad = conexion.execute("SELECT COUNT(*) FROM medicos").fetchone()[0]
        conexion.close()
        self.assertEqual(cantidad, 3)

    def test_conexion_segura_traduce_error_ocurrido_durante_el_uso(self):
        """
        obtener_conexion() ya traducia los errores al ABRIR la conexion.
        Este test cubre el caso que antes se escapaba: un error crudo de
        sqlite3 que ocurre DESPUES de abrir la conexion con exito (por
        ejemplo durante un cursor.execute()), que es el que antes llegaba
        crudo hasta metodos de los modelos sin try/except propio (listados,
        bajas logicas, etc).
        """
        crear_tablas()
        with self.assertRaises(BaseDeDatosCorruptaError):
            with conexion_segura() as conexion:
                raise sqlite3.DatabaseError("database disk image is malformed")

    def test_conexion_segura_traduce_error_de_bloqueo_ocurrido_durante_el_uso(self):
        crear_tablas()
        with self.assertRaises(BaseDeDatosBloqueadaError):
            with conexion_segura() as conexion:
                raise sqlite3.OperationalError("database is locked")

    def test_conexion_segura_deja_pasar_errores_de_integridad_sin_traducir(self):
        """
        Un error de integridad (ej: clave duplicada) no es un problema del
        archivo de base de datos, sino de los datos: no se traduce a
        BaseDeDatosCorruptaError, se deja pasar tal cual.
        """
        crear_tablas()
        with self.assertRaises(sqlite3.IntegrityError):
            with conexion_segura() as conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    """
                    INSERT INTO medicos (legajo, dni, nombre, apellido, especialidad, telefono, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("LEGDUP", "10000000", "Test", "Test", "Clinica", "111", "a@a.com"),
                )
                conexion.commit()
                cursor.execute(
                    """
                    INSERT INTO medicos (legajo, dni, nombre, apellido, especialidad, telefono, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("LEGDUP", "20000000", "Test", "Test", "Clinica", "111", "b@b.com"),
                )
                conexion.commit()

    def test_conexion_segura_cierra_la_conexion_aunque_falle(self):
        """
        La conexion se cierra siempre, haya error o no, para no dejar
        conexiones abiertas colgadas ante un fallo a mitad de operacion.
        """
        crear_tablas()
        conexion_capturada = {}
        try:
            with conexion_segura() as conexion:
                conexion_capturada["conexion"] = conexion
                raise sqlite3.DatabaseError("database disk image is malformed")
        except BaseDeDatosCorruptaError:
            pass

        with self.assertRaises(sqlite3.ProgrammingError):
            conexion_capturada["conexion"].execute("SELECT 1")


if __name__ == "__main__":
    unittest.main()
