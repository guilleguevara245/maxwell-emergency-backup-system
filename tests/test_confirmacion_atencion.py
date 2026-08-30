"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos del modelo ConfirmacionAtencion (codigo de turno
del sistema principal + DNI, registro libre e independiente de las
solicitudes locales).
"""

import os
import unittest

import database
from models.paciente import Paciente
from models.confirmacion_atencion import ConfirmacionAtencion


class TestConfirmacionAtencion(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()

        self.paciente = Paciente("Juan", "Perez", "12345678", "91122334455", "juan@test.com")
        self.paciente.guardar()

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)

    def test_guardar_confirmacion_valida(self):
        confirmacion = ConfirmacionAtencion("0809899", "12345678")
        confirmacion.guardar()
        self.assertIsNotNone(confirmacion.id)

    def test_codigo_de_turno_es_texto_libre(self):
        # No hay formato exigido: numeros, letras, guiones, todo vale.
        ConfirmacionAtencion("0809899", "12345678").guardar()
        ConfirmacionAtencion("TURNO-ABC-123", "12345678").guardar()
        ConfirmacionAtencion("abc", "12345678").guardar()
        self.assertEqual(len(ConfirmacionAtencion.listar_todas()), 3)

    def test_rechaza_codigo_vacio(self):
        with self.assertRaises(ValueError):
            ConfirmacionAtencion("", "12345678").guardar()

    def test_rechaza_paciente_inexistente(self):
        with self.assertRaises(ValueError):
            ConfirmacionAtencion("0809899", "99999999").guardar()

    def test_rechaza_paciente_inactivo(self):
        Paciente.eliminar("12345678")
        with self.assertRaises(ValueError):
            ConfirmacionAtencion("0809899", "12345678").guardar()

    def test_no_esta_exportada_por_defecto(self):
        confirmacion = ConfirmacionAtencion("0809899", "12345678")
        confirmacion.guardar()
        self.assertFalse(confirmacion.exportado)

    def test_contar_pendientes_de_exportar(self):
        ConfirmacionAtencion("0809899", "12345678").guardar()
        ConfirmacionAtencion("0809900", "12345678").guardar()
        self.assertEqual(ConfirmacionAtencion.contar_pendientes_de_exportar(), 2)

    def test_marcar_todas_como_exportadas_pone_contador_en_cero(self):
        ConfirmacionAtencion("0809899", "12345678").guardar()
        ConfirmacionAtencion.marcar_todas_como_exportadas()
        self.assertEqual(ConfirmacionAtencion.contar_pendientes_de_exportar(), 0)

    def test_listar_pendientes_de_exportar_devuelve_solo_las_no_exportadas(self):
        ConfirmacionAtencion("0809899", "12345678").guardar()
        ConfirmacionAtencion.marcar_todas_como_exportadas()
        ConfirmacionAtencion("0809900", "12345678").guardar()

        pendientes = ConfirmacionAtencion.listar_pendientes_de_exportar()
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0].codigo_turno, "0809900")

    def test_str_incluye_codigo_y_dni(self):
        confirmacion = ConfirmacionAtencion("0809899", "12345678")
        confirmacion.guardar()
        texto = str(confirmacion)
        self.assertIn("0809899", texto)
        self.assertIn("12345678", texto)


if __name__ == "__main__":
    unittest.main()
