"""
Maxwell Emergency Backup System - by Guillermo Guevara

Tests automaticos de utils/exportar.py: que la exportacion genere
los PDF, cree la carpeta con fecha, y borre los datos transitorios
(pacientes, solicitudes, confirmaciones) conservando los medicos.
"""

import os
import shutil
import unittest

import database
from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from models.confirmacion_atencion import ConfirmacionAtencion
from utils.exportar import (
    exportar_todo_pdf,
    CARPETA_EXPORTACION,
    listar_carpetas_respaldo,
    eliminar_carpeta_respaldo,
    eliminar_todas_las_carpetas_respaldo,
)


class TestExportarTodoPdf(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()

        Paciente("Juan", "Perez", "12345678", "1122334455", "juan@test.com").guardar()
        Medico("MED001", "87654321", "Ana", "Gomez", "Pediatria",
               "1133445566", "ana@test.com").guardar()
        Turno("12345678", "Pediatria", "Control", medico_legajo="MED001").guardar()
        ConfirmacionAtencion("0809899", "12345678").guardar()

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        if os.path.exists(CARPETA_EXPORTACION):
            shutil.rmtree(CARPETA_EXPORTACION)

    def test_exportar_todo_genera_los_4_pdf(self):
        rutas = exportar_todo_pdf()
        self.assertEqual(len(rutas), 4)
        for ruta in rutas:
            self.assertTrue(os.path.exists(ruta))

    def test_exportar_todo_borra_pacientes_turnos_y_confirmaciones(self):
        exportar_todo_pdf()
        self.assertEqual(Paciente.listar_todos(incluir_inactivos=True), [])
        self.assertEqual(Turno.listar_por_paciente("12345678"), [])
        self.assertEqual(ConfirmacionAtencion.listar_todas(), [])

    def test_exportar_todo_conserva_los_medicos(self):
        exportar_todo_pdf()
        medicos = Medico.listar_todos()
        self.assertEqual(len(medicos), 1)
        self.assertEqual(medicos[0].legajo, "MED001")

    def test_exportar_todo_no_rompe_si_no_hay_datos(self):
        # Despues de exportar y borrar, exportar de nuevo no debe fallar
        # aunque no haya pacientes ni turnos.
        exportar_todo_pdf()
        rutas = exportar_todo_pdf()
        self.assertEqual(len(rutas), 4)


class TestGestionDeRespaldos(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()
        if os.path.exists(CARPETA_EXPORTACION):
            shutil.rmtree(CARPETA_EXPORTACION)

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        if os.path.exists(CARPETA_EXPORTACION):
            shutil.rmtree(CARPETA_EXPORTACION)

    def test_listar_carpetas_respaldo_vacio_si_nunca_se_exporto(self):
        self.assertEqual(listar_carpetas_respaldo(), [])

    def test_listar_carpetas_respaldo_devuelve_las_generadas(self):
        os.makedirs(os.path.join(CARPETA_EXPORTACION, "registro de datos 01-01-2000 08-00"))
        os.makedirs(os.path.join(CARPETA_EXPORTACION, "registro de datos 02-01-2000 08-00"))
        self.assertEqual(len(listar_carpetas_respaldo()), 2)

    def test_eliminar_carpeta_respaldo_borra_la_carpeta(self):
        os.makedirs(os.path.join(CARPETA_EXPORTACION, "registro de datos 01-01-2000 08-00"))
        resultado = eliminar_carpeta_respaldo("registro de datos 01-01-2000 08-00")
        self.assertTrue(resultado)
        self.assertEqual(listar_carpetas_respaldo(), [])

    def test_eliminar_carpeta_respaldo_devuelve_false_si_no_existe(self):
        resultado = eliminar_carpeta_respaldo("no existe")
        self.assertFalse(resultado)

    def test_eliminar_todas_las_carpetas_respaldo(self):
        os.makedirs(os.path.join(CARPETA_EXPORTACION, "registro de datos 01-01-2000 08-00"))
        os.makedirs(os.path.join(CARPETA_EXPORTACION, "registro de datos 02-01-2000 08-00"))
        eliminar_todas_las_carpetas_respaldo()
        self.assertEqual(listar_carpetas_respaldo(), [])


if __name__ == "__main__":
    unittest.main()
