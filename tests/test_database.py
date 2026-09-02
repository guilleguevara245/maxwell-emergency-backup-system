"""
Maxwell Emergency Backup System - by Guillermo Guevara

Tests automaticos del modulo database: deteccion de un archivo de
base de datos corrupto y tolerancia a escrituras concurrentes desde
mas de una conexion (por ejemplo, dos instancias de Maxwell abiertas
al mismo tiempo por error).
"""

import os
import threading
import time
import unittest

import database
from database import (
    crear_tablas,
    obtener_conexion,
    BaseDeDatosCorruptaError,
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


if __name__ == "__main__":
    unittest.main()
