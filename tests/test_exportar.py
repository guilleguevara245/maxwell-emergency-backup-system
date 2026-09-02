"""
Maxwell Emergency Backup System - by Guillermo Guevara

Tests automaticos de utils/exportar.py: que la exportacion genere
los PDF, cree la carpeta con fecha, y borre los datos transitorios
(pacientes, solicitudes, confirmaciones) conservando los medicos.
"""

import os
import shutil
import subprocess
import sys
import unittest

import database
from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno
from models.confirmacion_atencion import ConfirmacionAtencion
from utils.exportar import (
    exportar_todo_pdf,
    CARPETA_EXPORTACION,
    CARPETA_ASSETS,
    listar_carpetas_respaldo,
    eliminar_carpeta_respaldo,
    eliminar_todas_las_carpetas_respaldo,
)


class TestCarpetaAssets(unittest.TestCase):
    """
    Regresion para el bug donde los PDF exportados salian sin logo al
    correr como ejecutable compilado: la ruta de "assets" era relativa
    al directorio de trabajo actual, que en un .exe --onefile de
    Nuitka es una carpeta temporal distinta en cada arranque.
    """

    def test_carpeta_assets_es_una_ruta_absoluta_que_existe(self):
        self.assertTrue(os.path.isabs(CARPETA_ASSETS))
        self.assertTrue(os.path.isdir(CARPETA_ASSETS))

    def test_carpeta_assets_se_resuelve_igual_sin_importar_el_directorio_de_trabajo(self):
        """
        Corre en un subproceso con el directorio de trabajo puesto en
        /tmp (o el temporal del sistema), imitando lo que le pasa a un
        .exe que se auto-extrae a una carpeta temporal: la ruta de
        assets no debe depender de "desde donde" se ejecuta Maxwell.
        """
        raiz_del_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        codigo = (
            "import sys; sys.path.insert(0, %r); "
            "from utils.exportar import CARPETA_ASSETS; "
            "import os; print(CARPETA_ASSETS); sys.exit(0 if os.path.isdir(CARPETA_ASSETS) else 1)"
        ) % raiz_del_proyecto

        directorio_ajeno = os.path.dirname(os.path.abspath(__file__))  # cualquier dir != raiz del proyecto
        resultado = subprocess.run(
            [sys.executable, "-c", codigo],
            cwd="/tmp" if os.path.isdir("/tmp") else directorio_ajeno,
            capture_output=True,
            text=True,
        )
        self.assertEqual(resultado.returncode, 0, msg=resultado.stdout + resultado.stderr)


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
