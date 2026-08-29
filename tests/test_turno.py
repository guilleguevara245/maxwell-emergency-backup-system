"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos del modelo Turno.
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

    def _crear_turno_valido(self, fecha="2026-09-01", hora="10:00"):
        return Turno("12345678", "MED001", fecha, hora, motivo="Control")

    def test_guardar_turno_valido(self):
        turno = self._crear_turno_valido()
        turno.guardar()
        self.assertIsNotNone(turno.id)
        self.assertEqual(turno.estado, "pendiente")

    def test_rechaza_motivo_vacio(self):
        turno = Turno("12345678", "MED001", "2026-09-01", "10:00", motivo="")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_fecha_con_formato_invalido(self):
        turno = Turno("12345678", "MED001", "01-09-2026", "10:00", motivo="Control")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_fecha_inexistente(self):
        turno = Turno("12345678", "MED001", "2026-02-30", "10:00", motivo="Control")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_rechaza_hora_con_formato_invalido(self):
        turno = Turno("12345678", "MED001", "2026-09-01", "25:99", motivo="Control")
        with self.assertRaises(ValueError):
            turno.guardar()

    def test_detecta_solapamiento_de_horario(self):
        self._crear_turno_valido().guardar()
        turno_solapado = self._crear_turno_valido()
        with self.assertRaises(ValueError):
            turno_solapado.guardar()

    def test_no_hay_solapamiento_en_horarios_distintos(self):
        self._crear_turno_valido(hora="10:00").guardar()
        turno_otro_horario = self._crear_turno_valido(hora="11:00")
        turno_otro_horario.guardar()
        self.assertIsNotNone(turno_otro_horario.id)

    def test_cancelar_libera_el_horario(self):
        turno = self._crear_turno_valido()
        turno.guardar()
        turno.cambiar_estado("cancelado")

        turno_nuevo = self._crear_turno_valido()
        turno_nuevo.guardar()  # no debe explotar: el horario cancelado queda libre
        self.assertIsNotNone(turno_nuevo.id)

    def test_cambiar_estado_a_ausente(self):
        turno = self._crear_turno_valido()
        turno.guardar()
        turno.cambiar_estado("ausente")
        self.assertEqual(turno.estado, "ausente")

    def test_cambiar_a_estado_invalido_lanza_error(self):
        turno = self._crear_turno_valido()
        turno.guardar()
        with self.assertRaises(ValueError):
            turno.cambiar_estado("no_existe")

    def test_resumen_por_paciente_cuenta_bien_los_estados(self):
        t1 = self._crear_turno_valido(fecha="2026-09-01"); t1.guardar()
        t2 = self._crear_turno_valido(fecha="2026-09-02"); t2.guardar()
        t3 = self._crear_turno_valido(fecha="2026-09-03"); t3.guardar()
        t1.cambiar_estado("atendido")
        t2.cambiar_estado("ausente")
        # t3 queda pendiente

        resumen, turnos = Turno.resumen_por_paciente("12345678")

        self.assertEqual(resumen["total"], 3)
        self.assertEqual(resumen["atendido"], 1)
        self.assertEqual(resumen["ausente"], 1)
        self.assertEqual(resumen["pendiente"], 1)
        self.assertEqual(len(turnos), 3)

    def test_listar_por_fecha_devuelve_solo_esa_fecha(self):
        self._crear_turno_valido(fecha="2026-09-01", hora="10:00").guardar()
        self._crear_turno_valido(fecha="2026-09-01", hora="11:00").guardar()
        self._crear_turno_valido(fecha="2026-09-02", hora="10:00").guardar()

        turnos = Turno.listar_por_fecha("2026-09-01")

        self.assertEqual(len(turnos), 2)

    def test_listar_por_fecha_sin_turnos_devuelve_lista_vacia(self):
        turnos = Turno.listar_por_fecha("2026-12-25")
        self.assertEqual(turnos, [])

    def test_listar_por_medico_devuelve_solo_los_de_ese_medico(self):
        Medico("MED002", "99887766", "Luis", "Diaz", "Cardiologia",
               "91122334455", "luis@test.com").guardar()
        self._crear_turno_valido(hora="10:00").guardar()
        Turno("12345678", "MED002", "2026-09-01", "11:00", motivo="Control").guardar()

        turnos_med001 = Turno.listar_por_medico("MED001")
        turnos_med002 = Turno.listar_por_medico("MED002")

        self.assertEqual(len(turnos_med001), 1)
        self.assertEqual(len(turnos_med002), 1)

    def test_buscar_por_id_encuentra_el_turno_correcto(self):
        turno = self._crear_turno_valido()
        turno.guardar()

        encontrado = Turno.buscar_por_id(turno.id)

        self.assertEqual(encontrado.paciente_dni, "12345678")
        self.assertEqual(encontrado.motivo, "Control")

    def test_buscar_por_id_devuelve_none_si_no_existe(self):
        self.assertIsNone(Turno.buscar_por_id(9999))

    def test_str_incluye_fecha_en_formato_visual(self):
        turno = self._crear_turno_valido(fecha="2026-09-01")
        turno.guardar()
        self.assertIn("01/09/2026", str(turno))


if __name__ == "__main__":
    unittest.main()
