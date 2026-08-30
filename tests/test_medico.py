"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos del modelo Medico.
"""

import os
import unittest

import database
from models.medico import Medico


class TestMedico(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)

    def _crear_medico_valido(self, legajo="MED001", dni="87654321"):
        return Medico(legajo, dni, "Ana", "Gomez", "Pediatria", "91133445566", "ana@test.com")

    def test_guardar_medico_valido(self):
        self._crear_medico_valido().guardar()
        encontrado = Medico.buscar_por_legajo("MED001")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.especialidad, "Pediatria")

    def test_no_permite_legajo_duplicado(self):
        self._crear_medico_valido().guardar()
        with self.assertRaises(Exception):
            Medico("MED001", "11223344", "Luis", "Diaz", "Cardiologia",
                   "91122334455", "luis@test.com").guardar()

    def test_no_permite_dni_duplicado_entre_medicos(self):
        self._crear_medico_valido().guardar()
        with self.assertRaises(Exception):
            Medico("MED002", "87654321", "Luis", "Diaz", "Cardiologia",
                   "91122334455", "luis@test.com").guardar()

    def test_rechaza_legajo_muy_corto(self):
        medico = Medico("AB", "11223344", "Luis", "Diaz", "Cardiologia",
                         "91122334455", "luis@test.com")
        with self.assertRaises(ValueError):
            medico.guardar()

    def test_rechaza_legajo_con_simbolos(self):
        medico = Medico("MED-01", "11223344", "Luis", "Diaz", "Cardiologia",
                         "91122334455", "luis@test.com")
        with self.assertRaises(ValueError):
            medico.guardar()

    def test_listar_por_especialidad_filtra_correctamente(self):
        self._crear_medico_valido("MED001", "11111111").guardar()
        Medico("MED002", "22222222", "Luis", "Diaz", "Cardiologia",
               "91122334455", "luis@test.com").guardar()

        pediatras = Medico.listar_por_especialidad("Pediatria")
        self.assertEqual(len(pediatras), 1)

    def test_listar_por_especialidad_no_distingue_mayusculas(self):
        self._crear_medico_valido().guardar()  # especialidad "Pediatria"

        self.assertEqual(len(Medico.listar_por_especialidad("pediatria")), 1)
        self.assertEqual(len(Medico.listar_por_especialidad("PEDIATRIA")), 1)
        self.assertEqual(len(Medico.listar_por_especialidad("PeDiAtRiA")), 1)

    def test_listar_todos_solo_muestra_activos_por_defecto(self):
        self._crear_medico_valido().guardar()
        Medico.eliminar("MED001")
        self.assertEqual(len(Medico.listar_todos()), 0)
        self.assertEqual(len(Medico.listar_todos(incluir_inactivos=True)), 1)

    def test_eliminar_es_borrado_logico(self):
        self._crear_medico_valido().guardar()
        Medico.eliminar("MED001")
        encontrado = Medico.buscar_por_legajo("MED001")
        self.assertIsNotNone(encontrado)
        self.assertFalse(encontrado.activo)

    def test_reactivar_vuelve_a_marcar_como_activo(self):
        self._crear_medico_valido().guardar()
        Medico.eliminar("MED001")
        Medico.reactivar("MED001")
        self.assertTrue(Medico.buscar_por_legajo("MED001").activo)

    def test_actualizar_modifica_los_datos(self):
        medico = self._crear_medico_valido()
        medico.guardar()
        medico.especialidad = "Cardiologia"
        medico.telefono = "91199988877"
        medico.actualizar()
        actualizado = Medico.buscar_por_legajo("MED001")
        self.assertEqual(actualizado.especialidad, "Cardiologia")
        self.assertEqual(actualizado.telefono, "91199988877")

    def test_str_muestra_inactivo_cuando_corresponde(self):
        self._crear_medico_valido().guardar()
        Medico.eliminar("MED001")
        texto = str(Medico.buscar_por_legajo("MED001"))
        self.assertIn("INACTIVO", texto)

    def test_str_no_muestra_inactivo_si_esta_activo(self):
        self._crear_medico_valido().guardar()
        texto = str(Medico.buscar_por_legajo("MED001"))
        self.assertNotIn("INACTIVO", texto)


if __name__ == "__main__":
    unittest.main()
