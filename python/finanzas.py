# Sistema de Gestión Financiera Personal - Python
# Montos en céntimos enteros; fechas como (mes, día) enteros.
import csv
from collections import namedtuple
from itertools import combinations
from math import sqrt
from pathlib import Path

Gasto = namedtuple("Gasto", "id mes dia cat cent")
Ingreso = namedtuple("Ingreso", "id mes dia cent")

# ---- Datos: se leen de datos/movimientos.csv (id,tipo,mes,dia,categoria,centimos) ----
RUTA_CSV = Path(__file__).resolve().parent.parent / "datos" / "movimientos.csv"


def cargar(ruta):
    gastos, ingresos = [], []
    with open(ruta, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            id_, mes, dia, cent = int(r["id"]), int(r["mes"]), int(r["dia"]), int(r["centimos"])
            if r["tipo"] == "GASTO":
                gastos.append(Gasto(id_, mes, dia, r["categoria"], cent))
            else:
                ingresos.append(Ingreso(id_, mes, dia, cent))
    return gastos, ingresos


gastos, ingresos = cargar(RUTA_CSV)

# ---- Parámetros ----
HOY_MES, HOY_DIA, DIAS_RESTANTES = 9, 20, 10
VENTANA_INI, VENTANA_DIAS = 14, 7
MICROGASTO, MIN_MICRO, RECORTE = 1000, 5, 0.2
SALDO_INICIAL, INGRESO_ESPERADO = 9000, 10000
CATEGORIAS = ["Comida", "Transporte", "Entretenimiento", "Servicios", "Otros"]
TOPE = {"Comida": 20000, "Transporte": 8000, "Entretenimiento": 12000, "Servicios": 20000, "Otros": 6000}


def soles(c):
    return f"{c / 100:.2f}"


# ---- Funcionalidades ----
# F1: total de gastos de una categoría en un mes (septiembre solo hasta HOY)
def total(mes, cat):
    return sum(g.cent for g in gastos if g.mes == mes and g.cat == cat and (mes < HOY_MES or g.dia <= HOY_DIA))


def f1():
    print("Categoría        Agosto  Septiembre")
    for c in CATEGORIAS:
        print(f"{c:<15s} {soles(total(8, c)):>8s} {soles(total(9, c)):>11s}")


# ¿El gasto cae en la ventana de análisis (días 14 al 20)?
def en_ventana(g):
    return g.mes == HOY_MES and VENTANA_INI <= g.dia <= HOY_DIA


# F2: microgastos de la ventana en Comida y Otros
def f2():
    print("Categoría  Microgastos   Total  ¿Patrón?")
    for c in ["Comida", "Otros"]:
        micro = [g.cent for g in gastos if en_ventana(g) and g.cat == c and g.cent < MICROGASTO]
        print(f"{c:<9s} {len(micro):11d} {soles(sum(micro)):>7s}  {'Sí' if len(micro) >= MIN_MICRO else 'No'}")


# F3: acumulado del mes de corte frente al tope; excedido = max(0, acumulado - tope)
def f3():
    print("Categoría        Acumulado    Tope  Excedido")
    for c in CATEGORIAS:
        acum = total(HOY_MES, c)
        print(f"{c:<15s} {soles(acum):>10s} {soles(TOPE[c]):>7s} {soles(max(0, acum - TOPE[c])):>9s}")


# F4: (n, media, desviación poblacional) de los gastos de agosto de una categoría
def stats(cat):
    x = [g.cent for g in gastos if g.mes == 8 and g.cat == cat]
    mu = sum(x) / len(x)
    return len(x), mu, sqrt(sum((v - mu) ** 2 for v in x) / len(x))


# Un gasto de septiembre es anómalo si supera media + 2 desviaciones de su categoría
def f4():
    print("Categoría        n   Media   Desv.  Umbral")
    for c in CATEGORIAS:
        n, mu, s = stats(c)
        print(f"{c:<15s} {n:2d} {soles(mu):>7s} {soles(s):>7s} {soles(mu + 2 * s):>7s}")
    print("Gastos anómalos:")
    for g in gastos:
        if g.mes == HOY_MES and g.dia <= HOY_DIA:
            _, mu, s = stats(g.cat)
            if g.cent > mu + 2 * s:
                print(f"  id {g.id} ({g.cat}, S/ {soles(g.cent)})")


# F5: proyección de liquidez (céntimos sin redondear; F6 reutiliza estos valores)
def hasta_hoy(mes, dia):
    return mes < HOY_MES or (mes == HOY_MES and dia <= HOY_DIA)


saldo_actual = (SALDO_INICIAL + sum(i.cent for i in ingresos if hasta_hoy(i.mes, i.dia))
                - sum(g.cent for g in gastos if hasta_hoy(g.mes, g.dia)))
gasto_variable = sum(g.cent for g in gastos if en_ventana(g) and g.cat != "Servicios")
gasto_diario = gasto_variable / VENTANA_DIAS
liquidez = saldo_actual + INGRESO_ESPERADO - gasto_diario * DIAS_RESTANTES


def f5():
    for nombre, v in [("Saldo actual", saldo_actual), ("Gasto variable de la ventana", gasto_variable),
                      ("Gasto diario proyectado", gasto_diario), ("Ingreso esperado restante", INGRESO_ESPERADO),
                      ("Liquidez a fin de mes", liquidez)]:
        print(f"{nombre:<30s} {soles(v):>8s}")
    print(f"Riesgo: {'sí' if liquidez < 0 else 'no'}")


# F6: plan de ahorro, solo si F5 detecta riesgo
def ahorro(cat):
    return sum(g.cent for g in gastos if en_ventana(g) and g.cat == cat) / VENTANA_DIAS * DIAS_RESTANTES * RECORTE


def f6():
    if liquidez >= 0:
        print("No hay riesgo de liquidez: el plan de ahorro no es necesario")
        return
    deficit = -liquidez
    rec = ["Comida", "Transporte", "Entretenimiento", "Otros"]

    def cumple(sub):
        return sum(ahorro(c) for c in sub) >= deficit

    print(f"Déficit: S/ {soles(deficit)}")
    for c in rec:
        print(f"{c:<16s} {soles(ahorro(c)):>7s}")
    print("Subconjunto                                    Ahorro  ¿Cumple?  ¿Mínimo?")
    for k in range(1, len(rec) + 1):
        for sub in combinations(rec, k):
            minimo = cumple(sub) and all(not cumple([x for x in sub if x != c]) for c in sub)
            print(f"{', '.join(sub):<45s} {soles(sum(ahorro(c) for c in sub)):>7s}  "
                  f"{'Sí' if cumple(sub) else 'No':<8s}  {'Sí' if minimo else '—'}")


# ---- Menú ----
def menu():
    opciones = {"1": f1, "2": f2, "3": f3, "4": f4, "5": f5, "6": f6}
    while True:
        print("\n1) F1 Total por categoría\n2) F2 Gasto hormiga\n3) F3 Exceso de presupuesto\n4) F4 Gastos anómalos"
              "\n5) F5 Liquidez a fin de mes\n6) F6 Plan de ahorro\n0) Salir")
        try:
            op = input().strip()
        except EOFError:
            op = "0"
        if op == "0":
            print("Hasta luego")
            break
        opciones.get(op, lambda: print("Opción no válida"))()


if __name__ == "__main__":
    menu()
