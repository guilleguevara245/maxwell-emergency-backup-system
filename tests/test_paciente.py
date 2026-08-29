"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos del modelo Paciente.
Usan una base de datos separada (test_maxwell_medic.db) para no
afectar los datos reales del sistema.
"""

import os
import unittest

import database
from models.paciente import Paciente


class TestPaciente(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)

    def _crear_paciente_valido(self, dni="12345678"):
        return Paciente("Juan", "Perez", dni, "91122334455", "juan@test.com")

    def test_guardar_paciente_valido(self):
        paciente = self._crear_paciente_valido()
        paciente.guardar()
        encontrado = Paciente.buscar_por_dni("12345678")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nombre, "Juan")

    def test_no_permite_dni_duplicado(self):
        self._crear_paciente_valido().guardar()
        with self.assertRaises(Exception):
            Paciente("Otro", "Nombre", "12345678", "91133445566", "otro@test.com").guardar()

    def test_rechaza_dni_con_letras(self):
        paciente = Paciente("X", "Y", "abc12345", "91122334455", "x@test.com")
        with self.assertRaises(ValueError):
            paciente.guardar()

    def test_rechaza_email_invalido(self):
        paciente = Paciente("X", "Y", "11223344", "91122334455", "no-es-email")
        with self.assertRaises(ValueError):
            paciente.guardar()

    def test_rechaza_telefono_celular_corto(self):
        paciente = Paciente("X", "Y", "22334455", "1122334455", "x@test.com")
        with self.assertRaises(ValueError):
            paciente.guardar()

    def test_acepta_sin_telefono_fijo(self):
        paciente = self._crear_paciente_valido("33445566")
        paciente.guardar()
        self.assertIsNone(Paciente.buscar_por_dni("33445566").telefono_fijo)

    def test_rechaza_telefono_fijo_corto_si_se_completa(self):
        paciente = Paciente("X", "Y", "44556677", "91122334455", "x@test.com", telefono_fijo="12345")
        with self.assertRaises(ValueError):
            paciente.guardar()

    def test_listar_todos_solo_muestra_activos_por_defecto(self):
        self._crear_paciente_valido("55667788").guardar()
        Paciente.eliminar("55667788")
        self.assertEqual(len(Paciente.listar_todos()), 0)
        self.assertEqual(len(Paciente.listar_todos(incluir_inactivos=True)), 1)

    def test_eliminar_es_borrado_logico_no_fisico(self):
        self._crear_paciente_valido("66778899").guardar()
        Paciente.eliminar("66778899")
        encontrado = Paciente.buscar_por_dni("66778899")
        self.assertIsNotNone(encontrado)  # sigue existiendo
        self.assertFalse(encontrado.activo)  # pero esta inactivo

    def test_reactivar_vuelve_a_marcar_como_activo(self):
        self._crear_paciente_valido("77889900").guardar()
        Paciente.eliminar("77889900")
        Paciente.reactivar("77889900")
        self.assertTrue(Paciente.buscar_por_dni("77889900").activo)

    def test_actualizar_modifica_los_datos(self):
        paciente = self._crear_paciente_valido("88990011")
        paciente.guardar()
        paciente.telefono = "91199988877"
        paciente.actualizar()
        self.assertEqual(Paciente.buscar_por_dni("88990011").telefono, "91199988877")


if __name__ == "__main__":
    unittest.main()
