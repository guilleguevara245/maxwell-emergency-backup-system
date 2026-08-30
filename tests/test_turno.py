"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos del modelo Turno (solicitudes de turno, sin
fecha ni hora: eso lo asigna despues el sistema principal).
"""

import os
import unittest

import database
from models.paciente import Paciente
from models.medico import Medico
from models.turno import Turno


class TestTurno(unittest.TestCase):

    def setUp(self):
        database.NOMBRE_BASE_DATOS = "test_maxwell_medic.db"
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)
        database.crear_tablas()

        self.paciente = Paciente("Juan", "Perez", "12345678", "91122334455", "juan@test.com")
        self.paciente.guardar()
        self.medico = Medico("MED001", "87654321", "Ana", "Gomez", "Pediatria",
                              "91133445566", "ana@test.com")
        self.medico.guardar()

    def tearDown(self):
        if os.path.exists(database.NOMBRE_BASE_DATOS):
            os.remove(database.NOMBRE_BASE_DATOS)

    def _crear_solicitud_valida(self, especialidad="Pediatria", medico_legajo=None):
        return Turno("12345678", especialidad, "Control", medico_legajo=medico_legajo)

    def test_guardar_solicitud_valida_sin_medico_especifico(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        self.assertIsNotNone(turno.id)
        self.assertEqual(turno.estado, "pendiente")
        self.assertIsNone(turno.medico_legajo)

    def test_guardar_solicitud_con_medico_especifico(self):
        turno = self._crear_solicitud_valida(medico_legajo="MED001")
        turno.guardar()
        self.assertEqual(turno.medico_legajo, "MED001")

    def test_guardar_solicitud_con_observaciones(self):
        turno = Turno("12345678", "Pediatria", "Control", observaciones="Alergia a la penicilina")
        turno.guardar()
        encontrada = Turno.buscar_por_id(turno.id)
        self.assertEqual(encontrada.observaciones, "Alergia a la penicilina")

    def test_observaciones_es_opcional(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        self.assertIsNone(turno.observaciones)

    def test_rechaza_motivo_vacio(self):
        turno = Turno("12345678", "Pediatria", "")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_especialidad_vacia(self):
        turno = Turno("12345678", "", "Control")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_solicitud_con_paciente_inexistente(self):
        turno = Turno("99999999", "Pediatria", "Control")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_solicitud_con_paciente_inactivo(self):
        Paciente.eliminar("12345678")
        turno = self._crear_solicitud_valida()
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_solicitud_con_medico_inexistente(self):
        turno = self._crear_solicitud_valida(medico_legajo="NOEXISTE")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_solicitud_con_medico_inactivo(self):
        Medico.eliminar("MED001")
        turno = self._crear_solicitud_valida(medico_legajo="MED001")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_permite_solicitud_sin_medico_aunque_no_haya_medicos_de_esa_especialidad(self):
        turno = self._crear_solicitud_valida(especialidad="Traumatologia")
        turno.guardar()
        self.assertIsNotNone(turno.id)

    def test_cambiar_a_estado_invalido_lanza_error(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        with self.assertRaises(ValueError):
            turno.cambiar_estado("no_existe")

    def test_ausente_ya_no_es_un_estado_valido(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        with self.assertRaises(ValueError):
            turno.cambiar_estado("ausente")

    def test_resumen_por_paciente_cuenta_bien_los_estados(self):
        t1 = self._crear_solicitud_valida(); t1.guardar()
        t2 = self._crear_solicitud_valida(); t2.guardar()
        t3 = self._crear_solicitud_valida(); t3.guardar()
        t1.cambiar_estado("atendido")
        t2.cambiar_estado("cancelado")
        # t3 queda pendiente

        resumen, turnos = Turno.resumen_por_paciente("12345678")

        self.assertEqual(resumen["total"], 3)
        self.assertEqual(resumen["atendido"], 1)
        self.assertEqual(resumen["cancelado"], 1)
        self.assertEqual(resumen["pendiente"], 1)
        self.assertEqual(len(turnos), 3)

    def test_listar_por_medico_devuelve_solo_los_de_ese_medico(self):
        Medico("MED002", "99887766", "Luis", "Diaz", "Cardiologia",
               "91122334455", "luis@test.com").guardar()
        self._crear_solicitud_valida(medico_legajo="MED001").guardar()
        Turno("12345678", "Cardiologia", "Control", medico_legajo="MED002").guardar()

        turnos_med001 = Turno.listar_por_medico("MED001")
        turnos_med002 = Turno.listar_por_medico("MED002")

        self.assertEqual(len(turnos_med001), 1)
        self.assertEqual(len(turnos_med002), 1)

    def test_listar_por_paciente_devuelve_todas_sus_solicitudes(self):
        self._crear_solicitud_valida().guardar()
        self._crear_solicitud_valida(especialidad="Cardiologia").guardar()

        turnos = Turno.listar_por_paciente("12345678")

        self.assertEqual(len(turnos), 2)

    def test_buscar_por_id_encuentra_la_solicitud_correcta(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()

        encontrado = Turno.buscar_por_id(turno.id)

        self.assertEqual(encontrado.paciente_dni, "12345678")
        self.assertEqual(encontrado.motivo, "Control")

    def test_buscar_por_id_devuelve_none_si_no_existe(self):
        self.assertIsNone(Turno.buscar_por_id(9999))

    def test_str_muestra_sin_medico_especifico_cuando_corresponde(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        self.assertIn("sin medico especifico", str(turno))

    def test_str_muestra_legajo_cuando_hay_medico_especifico(self):
        turno = self._crear_solicitud_valida(medico_legajo="MED001")
        turno.guardar()
        self.assertIn("MED001", str(turno))

    def test_solicitud_nueva_no_esta_exportada_por_defecto(self):
        turno = self._crear_solicitud_valida()
        turno.guardar()
        self.assertFalse(turno.exportado)

    def test_contar_pendientes_de_exportar(self):
        self._crear_solicitud_valida().guardar()
        self._crear_solicitud_valida(especialidad="Cardiologia").guardar()
        self.assertEqual(Turno.contar_pendientes_de_exportar(), 2)

    def test_marcar_todos_como_exportados_pone_contador_en_cero(self):
        self._crear_solicitud_valida().guardar()
        self._crear_solicitud_valida(especialidad="Cardiologia").guardar()
        Turno.marcar_todos_como_exportados()
        self.assertEqual(Turno.contar_pendientes_de_exportar(), 0)

    def test_listar_pendientes_de_exportar_devuelve_solo_los_no_exportados(self):
        self._crear_solicitud_valida().guardar()
        segunda = self._crear_solicitud_valida(especialidad="Cardiologia")
        segunda.guardar()

        Turno.marcar_todos_como_exportados()
        tercera = self._crear_solicitud_valida(especialidad="Traumatologia")
        tercera.guardar()

        pendientes = Turno.listar_pendientes_de_exportar()
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0].especialidad, "Traumatologia")

    def test_listar_de_hoy_devuelve_las_solicitudes_recien_creadas(self):
        self._crear_solicitud_valida().guardar()
        self._crear_solicitud_valida(especialidad="Cardiologia").guardar()

        de_hoy = Turno.listar_de_hoy()

        self.assertEqual(len(de_hoy), 2)

    def test_listar_de_hoy_vacio_si_no_hay_solicitudes(self):
        self.assertEqual(Turno.listar_de_hoy(), [])


if __name__ == "__main__":
    unittest.main()
