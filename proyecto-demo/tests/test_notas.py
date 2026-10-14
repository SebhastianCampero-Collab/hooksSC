"""Pruebas de las reglas de negocio. Están protegidas por un hook: nadie puede editarlas."""
import unittest

import notas

ESTUDIANTES = [
    {"nombre": "Ana", "nota": 85},
    {"nombre": "Luis", "nota": 51},
    {"nombre": "Sofia", "nota": 40},
    {"nombre": "Diego", "nota": 72},
]

# hola broooo


class TestPromedio(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(notas.calcular_promedio([60, 80, 100]), 80)

    def test_lista_vacia(self):
        with self.assertRaises(ValueError):
            notas.calcular_promedio([])


class TestNotaFinal(unittest.TestCase):
    def test_ponderacion_20_20_40_20(self):
        self.assertAlmostEqual(notas.nota_final(80, 70, 90, 100), 86)

    def test_maximo_es_100(self):
        self.assertAlmostEqual(notas.nota_final(100, 100, 100, 100), 100)


class TestAprobacion(unittest.TestCase):
    def test_51_aprueba(self):
        self.assertEqual(notas.estado(51), "APROBADO")

    def test_50_reprueba(self):
        self.assertEqual(notas.estado(50), "REPROBADO")

    def test_reportes(self):
        self.assertEqual(notas.reporte_aprobados(ESTUDIANTES), ["Ana", "Luis", "Diego"])
        self.assertEqual(notas.reporte_reprobados(ESTUDIANTES), ["Sofia"])


class TestValidacion(unittest.TestCase):
    def test_rango_valido(self):
        for nota in (0, 51, 100):
            self.assertTrue(notas.validar_nota(nota))

    def test_fuera_de_rango(self):
        for nota in (-1, 101):
            self.assertFalse(notas.validar_nota(nota))


class TestBusqueda(unittest.TestCase):
    def setUp(self):
        self.db = notas.crear_base_demo()

    def test_existente(self):
        self.assertEqual(len(notas.buscar_estudiante(self.db, "Ana")), 1)

    def test_inyeccion_sql(self):
        self.assertEqual(notas.buscar_estudiante(self.db, "x' OR '1'='1"), [])


class TestRanking(unittest.TestCase):
    def test_mejores_primero(self):
        nombres = [e["nombre"] for e in notas.mejores_estudiantes(ESTUDIANTES, 2)]
        self.assertEqual(nombres, ["Ana", "Diego"])


if __name__ == "__main__":
    unittest.main()
