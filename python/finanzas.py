# Sistema de Gestión Financiera Personal - Python (multiparadigma)
# Montos en céntimos enteros; fechas como (mes, día) enteros. Se redondea solo al imprimir.
#   - Orientado a objetos: Movimiento, Gasto e Ingreso (herencia y polimorfismo).
#   - Funcional: comprensiones, sum y all.
#   - Imperativo: bucles y condicionales en la carga, los reportes y el menú.
import csv
from itertools import combinations
from math import sqrt
from pathlib import Path

# ---- Parámetros (ver datos/especificacion-sistema.md, sección 3) ----
RUTA_CSV = Path(__file__).resolve().parent.parent / "datos" / "movimientos.csv"
HOY_MES, HOY_DIA, DIAS_RESTANTES = 9, 20, 10
MES_BASE = 8  # mes de la línea base de F4
VENTANA_INI, VENTANA_DIAS = 14, 7
MICROGASTO, MIN_MICRO, RECORTE = 1000, 5, 0.2
SALDO_INICIAL, INGRESO_ESPERADO = 9000, 10000
CATEGORIAS = ["Comida", "Transporte", "Entretenimiento", "Servicios", "Otros"]
CAT_HORMIGA = ["Comida", "Otros"]
CAT_FIJA = "Servicios"  # gasto fijo: no entra en el gasto diario ni se puede recortar
CAT_RECORTABLES = [c for c in CATEGORIAS if c != CAT_FIJA]
TOPE = {"Comida": 20000, "Transporte": 8000, "Entretenimiento": 12000, "Servicios": 20000, "Otros": 6000}


# ---- Modelo de datos (orientado a objetos) ----
class Movimiento:
    """Movimiento de dinero: base común de Gasto e Ingreso."""

    def __init__(self, id_, mes, dia, centimos):
        self.id = id_
        self.mes = mes
        self.dia = dia
        self.centimos = centimos

    def hasta_hoy(self):
        """¿Ocurrió en la fecha de corte o antes?"""
        return self.mes < HOY_MES or (self.mes == HOY_MES and self.dia <= HOY_DIA)

    def efecto_saldo(self):
        """Cuánto cambia el saldo (en céntimos); cada subclase define su signo."""
        raise NotImplementedError


class Ingreso(Movimiento):
    def efecto_saldo(self):
        return self.centimos


class Gasto(Movimiento):
    def __init__(self, id_, mes, dia, categoria, centimos):
        super().__init__(id_, mes, dia, centimos)
        self.categoria = categoria

    def efecto_saldo(self):
        return -self.centimos

    def en_ventana(self):
        """¿Cae en la ventana de análisis (días 14 al 20 del mes de corte)?"""
        return self.mes == HOY_MES and VENTANA_INI <= self.dia <= HOY_DIA

    def es_microgasto(self):
        return self.centimos < MICROGASTO


# ---- Carga: lee el CSV (id,tipo,mes,dia,categoria,centimos) y devuelve una lista de Movimiento ----
def cargar(ruta):
    movimientos = []
    with open(ruta, encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            id_, mes, dia, cent = int(fila["id"]), int(fila["mes"]), int(fila["dia"]), int(fila["centimos"])
            if fila["tipo"] == "GASTO":
                movimientos.append(Gasto(id_, mes, dia, fila["categoria"], cent))
            else:
                movimientos.append(Ingreso(id_, mes, dia, cent))
    return movimientos


def solo_gastos(movimientos):
    return [m for m in movimientos if isinstance(m, Gasto)]


def soles(c):
    return f"{c / 100:.2f}"


# ---- Funcionalidades ----
# F1: total de gastos de una categoría en un mes (septiembre solo hasta HOY)
def total(movimientos, mes, cat):
    acumulado = 0
    for g in solo_gastos(movimientos):
        # Septiembre solo cuenta hasta la fecha de corte (hasta_hoy)
        if g.mes == mes and g.categoria == cat and g.hasta_hoy():
            acumulado += g.centimos
    return acumulado


def f1(movimientos):
    print("Categoría        Agosto  Septiembre")
    for c in CATEGORIAS:
        print(f"{c:<15s} {soles(total(movimientos, MES_BASE, c)):>8s} {soles(total(movimientos, HOY_MES, c)):>11s}")


# F2: microgastos de la ventana en las categorías sujetas a gasto hormiga
def f2(movimientos):
    print("Categoría  Microgastos   Total  ¿Patrón?")
    for c in CAT_HORMIGA:
        contador, acumulado = 0, 0
        for g in solo_gastos(movimientos):
            if g.en_ventana() and g.categoria == c and g.es_microgasto():
                contador += 1
                acumulado += g.centimos
        # Hay patrón de gasto hormiga con MIN_MICRO microgastos o más en la ventana
        patron = "Sí" if contador >= MIN_MICRO else "No"
        print(f"{c:<9s} {contador:11d} {soles(acumulado):>7s}  {patron}")


# F3: acumulado del mes de corte frente al tope; excedido = acumulado - tope si lo supera, si no 0
def f3(movimientos):
    print("Categoría        Acumulado    Tope  Excedido")
    for c in CATEGORIAS:
        acum = total(movimientos, HOY_MES, c)
        excedido = 0
        if acum > TOPE[c]:  # solo hay exceso si el acumulado supera el tope
            excedido = acum - TOPE[c]
        print(f"{c:<15s} {soles(acum):>10s} {soles(TOPE[c]):>7s} {soles(excedido):>9s}")


# F4: (n, media, desviación poblacional) de los gastos de agosto de una categoría
def estadisticas(movimientos, cat):
    n, suma = 0, 0
    for g in solo_gastos(movimientos):
        if g.mes == MES_BASE and g.categoria == cat:
            n += 1
            suma += g.centimos
    mu = suma / n
    suma_cuadrados = 0
    for g in solo_gastos(movimientos):
        if g.mes == MES_BASE and g.categoria == cat:
            suma_cuadrados += (g.centimos - mu) ** 2
    return n, mu, sqrt(suma_cuadrados / n)  # poblacional: se divide entre n, no n - 1


# Umbral de anomalía: media + 2 desviaciones (σ poblacional, se divide entre n)
def umbral(mu, s):
    return mu + 2 * s


def f4(movimientos):
    print("Categoría        n   Media   Desv.  Umbral")
    umbrales = {}  # un solo cálculo por categoría: la tabla y el filtro usan el mismo umbral
    for c in CATEGORIAS:
        n, mu, s = estadisticas(movimientos, c)
        umbrales[c] = umbral(mu, s)
        print(f"{c:<15s} {n:2d} {soles(mu):>7s} {soles(s):>7s} {soles(umbrales[c]):>7s}")
    print("Gastos anómalos:")
    # Se filtran los gastos de septiembre hasta HOY que superan el umbral de su categoría
    for g in solo_gastos(movimientos):
        if g.mes == HOY_MES and g.hasta_hoy() and g.centimos > umbrales[g.categoria]:
            print(f"  id {g.id} ({g.categoria}, S/ {soles(g.centimos)})")


# F5: proyección de liquidez (céntimos sin redondear; F6 reutiliza estos valores)
def proyeccion(movimientos):
    """Devuelve (saldo_actual, gasto_variable, gasto_diario, liquidez_fin)."""
    saldo = SALDO_INICIAL + sum(m.efecto_saldo() for m in movimientos if m.hasta_hoy())
    # Servicios se excluye: es un gasto fijo que ya se pagó en el mes
    variable = sum(g.centimos for g in solo_gastos(movimientos) if g.en_ventana() and g.categoria != CAT_FIJA)
    diario = variable / VENTANA_DIAS
    return saldo, variable, diario, saldo + INGRESO_ESPERADO - diario * DIAS_RESTANTES


def f5(movimientos):
    saldo, variable, diario, liquidez = proyeccion(movimientos)
    for nombre, v in [("Saldo actual", saldo), ("Gasto variable de la ventana", variable),
                      ("Gasto diario proyectado", diario), ("Ingreso esperado restante", INGRESO_ESPERADO),
                      ("Liquidez a fin de mes", liquidez)]:
        print(f"{nombre:<30s} {soles(v):>8s}")
    print(f"Riesgo: {'sí' if liquidez < 0 else 'no'}")


# F6: plan de ahorro, solo si F5 detecta riesgo
# Ahorro de una categoría = gasto diario de la ventana × días restantes × 20 %
def ahorro(movimientos, cat):
    en_ventana = sum(g.centimos for g in solo_gastos(movimientos) if g.en_ventana() and g.categoria == cat)
    return en_ventana / VENTANA_DIAS * DIAS_RESTANTES * RECORTE


def f6(movimientos):
    liquidez = proyeccion(movimientos)[3]
    if liquidez >= 0:
        print("No hay riesgo de liquidez: el plan de ahorro no es necesario")
        return
    deficit = -liquidez
    por_cat = {c: ahorro(movimientos, c) for c in CAT_RECORTABLES}

    def cumple(sub):
        return sum(por_cat[c] for c in sub) >= deficit

    print(f"Déficit: S/ {soles(deficit)}")
    for c in CAT_RECORTABLES:
        print(f"{c:<16s} {soles(por_cat[c]):>7s}")
    print("Subconjunto                                    Ahorro  ¿Cumple?  ¿Mínimo?")
    for k in range(1, len(CAT_RECORTABLES) + 1):
        for sub in combinations(CAT_RECORTABLES, k):
            # Mínima: cumple y ningún subconjunto propio cumple (basta quitar un elemento)
            minimo = cumple(sub) and all(not cumple([x for x in sub if x != c]) for c in sub)
            print(f"{', '.join(sub):<45s} {soles(sum(por_cat[c] for c in sub)):>7s}  "
                  f"{'Sí' if cumple(sub) else 'No':<8s}  {'Sí' if minimo else '—'}")


# ---- Menú ----
def menu(movimientos):
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
        if op in opciones:
            opciones[op](movimientos)
        else:
            print("Opción no válida")


if __name__ == "__main__":
    menu(cargar(RUTA_CSV))
