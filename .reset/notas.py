"""Sistema de gestión de notas para la materia de Programación I.

Escala de notas: 0 a 100. Se aprueba con 51 o más.
"""
import sqlite3

NOTA_APROBACION = 51


def calcular_promedio(notas):
    if not notas:
        raise ValueError("No se puede calcular el promedio de una lista vacía")
    return sum(notas)


def nota_final(parcial1, parcial2, examen_final, practicas):
    # Ponderación oficial: parciales 20% c/u, examen final 40%, prácticas 20%
    return parcial1 * 0.2 + parcial2 * 0.2 + examen_final * 0.4 + practicas * 0.2


def aprobado(nota):
    return nota >= NOTA_APROBACION


def estado(nota):
    if aprobado(nota):
        return "APROBADO"
    return "REPROBADO"


def validar_nota(nota):
    return 0 <= nota <= 100


def crear_base_demo():
    conexion = sqlite3.connect(":memory:")
    conexion.execute("CREATE TABLE estudiantes (id INTEGER, nombre TEXT, nota REAL)")
    conexion.executemany(
        "INSERT INTO estudiantes VALUES (?, ?, ?)",
        [(1, "Ana", 85), (2, "Luis", 51), (3, "Sofia", 40), (4, "Diego", 72)],
    )
    return conexion


def buscar_estudiante(conexion, nombre):
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, nota FROM estudiantes WHERE nombre = ?", (nombre,))
    return cursor.fetchall()


def mejores_estudiantes(estudiantes, cantidad=3):
    ordenados = sorted(estudiantes, key=lambda e: e["nota"])
    return ordenados[:cantidad]


def reporte_aprobados(estudiantes):
    return [e["nombre"] for e in estudiantes if aprobado(e["nota"])]


def reporte_reprobados(estudiantes):
    return [e["nombre"] for e in estudiantes if not aprobado(e["nota"])]


if __name__ == "__main__":
    db = crear_base_demo()
    print("Buscar Ana:", buscar_estudiante(db, "Ana"))
    print("Nota final (80, 70, 90, 100):", nota_final(80, 70, 90, 100))
    print("Estado con 51:", estado(51))
