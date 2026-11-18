# Sistema de Gestión Financiera Personal - Python
# Montos en céntimos enteros; fechas como (mes, día) enteros.
from collections import namedtuple
from itertools import combinations
from math import sqrt

Gasto = namedtuple("Gasto", "id mes dia cat cent")
Ingreso = namedtuple("Ingreso", "id mes dia cent")

# ---- Datos (mismos 80 movimientos de datos/movimientos.csv) ----
gastos = [Gasto(*g) for g in [
    (2,8,1,"Comida",980), (3,8,2,"Comida",920), (4,8,2,"Transporte",500), (5,8,3,"Comida",700),
    (6,8,3,"Otros",1950), (7,8,4,"Transporte",550), (8,8,5,"Comida",830), (9,8,5,"Servicios",3500),
    (10,8,6,"Comida",1340), (11,8,7,"Transporte",450), (12,8,7,"Servicios",8000), (13,8,8,"Comida",960),
    (14,8,8,"Entretenimiento",2000), (15,8,9,"Comida",1250), (16,8,9,"Otros",650), (17,8,10,"Transporte",500),
    (18,8,10,"Servicios",6000), (19,8,11,"Comida",1080), (20,8,12,"Comida",1500), (21,8,13,"Transporte",450),
    (22,8,13,"Otros",2000), (23,8,14,"Comida",1060), (24,8,15,"Transporte",400), (25,8,15,"Entretenimiento",2500),
    (26,8,16,"Comida",1100), (27,8,17,"Comida",1280), (28,8,18,"Otros",650), (29,8,19,"Comida",1100),
    (30,8,20,"Transporte",500), (32,8,21,"Comida",1390), (33,8,22,"Entretenimiento",3000), (34,8,23,"Comida",1350),
    (35,8,24,"Transporte",500), (36,8,25,"Comida",1630), (37,8,26,"Otros",1750), (38,8,27,"Comida",1410),
    (39,8,28,"Transporte",400), (40,8,29,"Comida",1220), (41,8,29,"Entretenimiento",3500), (42,8,30,"Otros",850),
    (43,8,31,"Comida",920), (45,9,1,"Comida",1400), (46,9,2,"Servicios",8500), (47,9,2,"Comida",1350),
    (48,9,3,"Servicios",6200), (49,9,3,"Transporte",550), (50,9,4,"Servicios",3000), (51,9,4,"Comida",1200),
    (52,9,5,"Entretenimiento",3500), (53,9,5,"Otros",2000), (54,9,6,"Comida",1550), (55,9,6,"Transporte",450),
    (56,9,7,"Transporte",2800), (57,9,7,"Comida",1600), (58,9,8,"Comida",1300), (59,9,8,"Entretenimiento",2500),
    (60,9,9,"Transporte",500), (61,9,9,"Otros",1400), (62,9,10,"Comida",1450), (63,9,10,"Transporte",300),
    (65,9,13,"Comida",3800), (66,9,13,"Comida",1300), (67,9,14,"Comida",750), (68,9,14,"Transporte",300),
    (69,9,15,"Comida",850), (70,9,15,"Otros",650), (71,9,16,"Comida",900), (72,9,16,"Transporte",300),
    (73,9,17,"Comida",650), (74,9,17,"Otros",500), (75,9,18,"Comida",800), (76,9,18,"Transporte",300),
    (77,9,19,"Comida",950), (78,9,19,"Entretenimiento",9500), (79,9,20,"Comida",700), (80,9,20,"Otros",700),
]]
ingresos = [Ingreso(1,8,1,55000), Ingreso(31,8,21,10000), Ingreso(44,9,1,55000), Ingreso(64,9,12,10000)]

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
