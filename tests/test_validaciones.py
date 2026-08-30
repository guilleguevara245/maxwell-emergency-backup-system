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
)


class TestValidarDni(unittest.TestCase):
    def test_dni_valido_no_lanza_error(self):
        validar_dni("12345678")

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
    def test_celular_de_10_digitos_no_lanza_error(self):
        validar_telefono("1122334455")

    def test_celular_de_9_digitos_lanza_error(self):
        with self.assertRaises(ValueError):
            validar_telefono("112233445")

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


if __name__ == "__main__":
    unittest.main()
