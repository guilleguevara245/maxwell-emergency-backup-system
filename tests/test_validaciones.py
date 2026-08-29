"""
Maxwell Medic System - by Guillermo Guevara

Tests automaticos de las funciones de utils/validaciones.py.
Son funciones puras (no usan la base de datos), por eso no necesitan
setUp/tearDown con base de datos de prueba.
"""

import unittest

from utils.validaciones import (
    validar_legajo,
    validar_dni,
    validar_email,
    validar_telefono,
    validar_telefono_fijo,
    validar_fecha,
    validar_hora,
    fecha_visual_a_iso,
    fecha_iso_a_visual,
)


class TestValidarDni(unittest.TestCase):
    def test_dni_valido_no_lanza_error(self):
        validar_dni("12345678")  # no debe lanzar excepcion

    def test_dni_con_letras_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_dni("1234abc8")

    def test_dni_muy_corto_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_dni("123456")

    def test_dni_muy_largo_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_dni("123456789")


class TestValidarEmail(unittest.TestCase):
    def test_email_valido_no_lanza_error(self):
        validar_email("juan@test.com")

    def test_email_sin_arroba_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_email("juan-test.com")

    def test_email_sin_dominio_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_email("juan@test")


class TestValidarTelefono(unittest.TestCase):
    def test_celular_de_11_digitos_no_lanza_error(self):
        validar_telefono("91122334455")

    def test_celular_de_10_digitos_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_telefono("1122334455")

    def test_telefono_vacio_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_telefono("")


class TestValidarTelefonoFijo(unittest.TestCase):
    def test_fijo_vacio_no_lanza_error_porque_es_opcional(self):
        validar_telefono_fijo(None)
        validar_telefono_fijo("")

    def test_fijo_de_10_digitos_no_lanza_error(self):
        validar_telefono_fijo("1145678900")

    def test_fijo_muy_corto_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_telefono_fijo("12345")


class TestValidarLegajo(unittest.TestCase):
    def test_legajo_valido_no_lanza_error(self):
        validar_legajo("MED001")

    def test_legajo_vacio_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_legajo("")

    def test_legajo_muy_corto_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_legajo("AB")

    def test_legajo_muy_largo_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_legajo("A" * 11)

    def test_legajo_con_simbolos_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_legajo("MED-01")


class TestValidarFechaYHora(unittest.TestCase):
    def test_fecha_valida_no_lanza_error(self):
        validar_fecha("2026-09-01")

    def test_fecha_formato_incorrecto_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_fecha("01-09-2026")

    def test_fecha_inexistente_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_fecha("2026-02-30")

    def test_hora_valida_no_lanza_error(self):
        validar_hora("10:00")

    def test_hora_formato_incorrecto_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_hora("25:99")


class TestConversionFechas(unittest.TestCase):
    def test_fecha_visual_a_iso_convierte_correctamente(self):
        self.assertEqual(fecha_visual_a_iso("01/09/2026"), "2026-09-01")

    def test_fecha_visual_a_iso_rechaza_formato_incorrecto(self):
        with self.assertRaises(ValueError):
            fecha_visual_a_iso("2026-09-01")

    def test_fecha_iso_a_visual_convierte_correctamente(self):
        self.assertEqual(fecha_iso_a_visual("2026-09-01"), "01/09/2026")

    def test_conversion_ida_y_vuelta_da_el_mismo_resultado(self):
        original = "25/12/2026"
        iso = fecha_visual_a_iso(original)
        de_vuelta = fecha_iso_a_visual(iso)
        self.assertEqual(original, de_vuelta)


if __name__ == "__main__":
    unittest.main()
