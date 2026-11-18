"""Verifica que Python, Scala y Prolog reproduzcan las tablas de la sección 5 de
datos/especificacion-sistema.md.

Cada programa se ejecuta como proceso, con el menú alimentado por la entrada estándar
(opciones 1 a 6 y 0). La salida se divide por opción y se compara con lo esperado.

Reglas de comparación (sección 6 de la especificación), todo en céntimos:
  - F1, F2 y F3: igualdad exacta.
  - F4, F5 y F6: tolerancia de ±0.01 soles (1 céntimo).

Uso (desde cualquier carpeta):
    python3 tests/verificar.py                  # los tres lenguajes
    python3 tests/verificar.py python prolog    # solo los indicados
Código de salida: 0 todo bien; 1 hay diferencias; 2 algún lenguaje no se pudo ejecutar.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOL_EXACTA, TOL_ESTADISTICA = 0, 1  # en céntimos

# ---- Resultados esperados (sección 5 de la especificación), en céntimos ----
CATEGORIAS = ["Comida", "Transporte", "Entretenimiento", "Servicios", "Otros"]

F1 = {  # categoría: (agosto, septiembre hasta el día 20)
    "Comida": (22020, 20550), "Transporte": (4250, 5500), "Entretenimiento": (11000, 15500),
    "Servicios": (17500, 17700), "Otros": (7850, 5250),
}
F2 = {"Comida": (7, 5600, True), "Otros": (3, 1850, False)}  # microgastos, total, ¿patrón?
F3 = {  # acumulado, tope, excedido
    "Comida": (20550, 20000, 550), "Transporte": (5500, 8000, 0), "Entretenimiento": (15500, 12000, 3500),
    "Servicios": (17700, 20000, 0), "Otros": (5250, 6000, 0),
}
F4 = {  # n base, media, desviación, umbral
    "Comida": (19, 1159, 238, 1635), "Transporte": (9, 472, 48, 568), "Entretenimiento": (4, 2750, 559, 3868),
    "Servicios": (3, 5833, 1841, 9515), "Otros": (6, 1308, 600, 2509),
}
F4_ANOMALOS = {(65, "Comida", 3800), (56, "Transporte", 2800), (78, "Entretenimiento", 9500)}
F5 = {
    "Saldo actual": 11880, "Gasto variable de la ventana": 17850, "Gasto diario proyectado": 2550,
    "Ingreso esperado restante": 10000, "Liquidez a fin de mes": -3620,
}
F6_DEFICIT = 3620
F6_AHORRO = {"Comida": 1600, "Transporte": 257, "Entretenimiento": 2714, "Otros": 529}
F6_SUBCONJUNTOS = {  # subconjunto: (ahorro, ¿cumple?, ¿mínimo?)
    ("Comida",): (1600, False, False), ("Transporte",): (257, False, False),
    ("Entretenimiento",): (2714, False, False), ("Otros",): (529, False, False),
    ("Comida", "Transporte"): (1857, False, False), ("Comida", "Entretenimiento"): (4314, True, True),
    ("Comida", "Otros"): (2129, False, False), ("Transporte", "Entretenimiento"): (2971, False, False),
    ("Transporte", "Otros"): (786, False, False), ("Entretenimiento", "Otros"): (3243, False, False),
    ("Comida", "Transporte", "Entretenimiento"): (4571, True, False),
    ("Comida", "Transporte", "Otros"): (2386, False, False),
    ("Comida", "Entretenimiento", "Otros"): (4843, True, False),
    ("Transporte", "Entretenimiento", "Otros"): (3500, False, False),
    ("Comida", "Transporte", "Entretenimiento", "Otros"): (5100, True, False),
}


# ---- Ejecución de cada programa ----
MENU_INICIO = re.compile(r"^1\) F1 Total por categoría")
RUIDO_SBT = re.compile(r"^\[(info|warn|error|success)\]")


def comando(lenguaje):
    """Devuelve (carpeta de trabajo, comando) o None si falta la herramienta."""
    if lenguaje == "python":
        return RAIZ, [sys.executable, "python/finanzas.py"]
    if lenguaje == "prolog":
        return (RAIZ, ["swipl", "prolog/finanzas.pl"]) if shutil.which("swipl") else None
    # Scala solo resuelve "../datos/movimientos.csv" desde scala/
    return (RAIZ / "scala", [shutil.which("sbt"), "run"]) if shutil.which("sbt") else None


def ejecutar(lenguaje):
    """Corre el programa una vez con las opciones 1..6 y 0; devuelve la salida de cada opción."""
    destino = comando(lenguaje)
    if destino is None:
        return None
    carpeta, cmd = destino
    entrada = "".join(f"{op}\n" for op in (1, 2, 3, 4, 5, 6, 0))
    proc = subprocess.run(cmd, cwd=carpeta, input=entrada, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600, env={**os.environ, "LC_ALL": "C.UTF-8"})
    return separar_por_opcion(proc.stdout)


def separar_por_opcion(salida):
    """Cada menú impreso abre una sección; la sección k trae el resultado de la opción k-1."""
    secciones, actual = [], None
    for linea in salida.splitlines():
        if MENU_INICIO.match(linea):
            actual = []
            secciones.append(actual)
        elif actual is not None and not RUIDO_SBT.match(linea) and not re.match(r"^\d\) F\d |^0\) Salir", linea):
            actual.append(linea.rstrip())
    # secciones[0] es la salida de la opción 1 (se imprime tras el primer menú), etc.
    return {op: [l for l in secciones[op - 1] if l.strip()] for op in range(1, 7) if op <= len(secciones)}


# ---- Lectura de números impresos ----
def centimos(texto):
    return round(float(texto) * 100)


def tokens(linea):
    return linea.split()


def leer_f1(lineas):
    out = {}
    for l in lineas:
        t = tokens(l)
        if len(t) == 3 and t[0] in CATEGORIAS:
            out[t[0]] = (centimos(t[1]), centimos(t[2]))
    return out


def leer_f2(lineas):
    out = {}
    for l in lineas:
        t = tokens(l)
        if len(t) == 4 and t[0] in CATEGORIAS:
            out[t[0]] = (int(t[1]), centimos(t[2]), t[3] == "Sí")
    return out


def leer_f3(lineas):
    out = {}
    for l in lineas:
        t = tokens(l)
        if len(t) == 4 and t[0] in CATEGORIAS:
            out[t[0]] = tuple(centimos(x) for x in t[1:])
    return out


def leer_f4(lineas):
    base, anomalos = {}, set()
    for l in lineas:
        t = tokens(l)
        if len(t) == 5 and t[0] in CATEGORIAS:
            base[t[0]] = (int(t[1]),) + tuple(centimos(x) for x in t[2:])
        m = re.match(r"\s*id (\d+) \((\w+), S/ (\d+\.\d\d)\)", l)
        if m:
            anomalos.add((int(m[1]), m[2], centimos(m[3])))
    return base, anomalos


def leer_f5(lineas):
    out, riesgo = {}, None
    for l in lineas:
        m = re.match(r"^(.+?)\s+(-?\d+\.\d\d)$", l.strip())
        if m:
            out[m[1]] = centimos(m[2])
        m = re.match(r"^Riesgo:\s*(\S+)", l.strip())
        if m:
            riesgo = m[1].lower() in ("sí", "si")
    return out, riesgo


def leer_f6(lineas):
    deficit, ahorro, filas = None, {}, {}
    for l in lineas:
        m = re.match(r"^Déficit: S/ (\d+\.\d\d)", l)
        if m:
            deficit = centimos(m[1])
        m = re.match(r"^(\w+)\s+(\d+\.\d\d)$", l.strip())
        if m:
            ahorro[m[1]] = centimos(m[2])
        m = re.match(r"^(.+?)\s+(\d+\.\d\d)\s+(Sí|No)\s+(Sí|—)$", l.strip())
        if m:
            sub = tuple(x.strip() for x in m[1].split(","))
            filas[sub] = (centimos(m[2]), m[3] == "Sí", m[4] == "Sí")
    return deficit, ahorro, filas


# ---- Comparaciones ----
class Resultado:
    def __init__(self):
        self.comprobaciones = 0
        self.fallos = []

    def igual(self, nombre, obtenido, esperado, tol=TOL_EXACTA):
        self.comprobaciones += 1
        if isinstance(esperado, int) and not isinstance(esperado, bool) and isinstance(obtenido, int):
            ok = abs(obtenido - esperado) <= tol
        else:
            ok = obtenido == esperado
        if not ok:
            self.fallos.append(f"{nombre}: obtenido {obtenido!r}, esperado {esperado!r} (tolerancia {tol} céntimos)")


def comparar_tabla(res, f, obtenido, esperado, tols):
    """Compara fila a fila; tols da la tolerancia de cada columna."""
    for cat, fila_esp in esperado.items():
        fila_obt = obtenido.get(cat)
        if fila_obt is None:
            res.fallos.append(f"{f} {cat}: fila ausente")
            res.comprobaciones += 1
            continue
        for i, (o, e) in enumerate(zip(fila_obt, fila_esp)):
            res.igual(f"{f} {cat} col{i + 1}", o, e, tols[i])


def verificar(salidas):
    res = Resultado()
    for f, op in (("F1", 1), ("F2", 2), ("F3", 3), ("F4", 4), ("F5", 5), ("F6", 6)):
        if op not in salidas or not salidas[op]:
            res.fallos.append(f"{f}: sin salida")
            res.comprobaciones += 1
    if res.fallos:
        return res
    comparar_tabla(res, "F1", leer_f1(salidas[1]), F1, (0, 0))
    comparar_tabla(res, "F2", leer_f2(salidas[2]), F2, (0, 0, 0))
    comparar_tabla(res, "F3", leer_f3(salidas[3]), F3, (0, 0, 0))
    base, anomalos = leer_f4(salidas[4])
    comparar_tabla(res, "F4", base, F4, (0, 1, 1, 1))
    res.igual("F4 anómalos", anomalos, F4_ANOMALOS)
    valores, riesgo = leer_f5(salidas[5])
    for nombre, esperado in F5.items():
        res.igual(f"F5 {nombre}", valores.get(nombre), esperado, TOL_ESTADISTICA)
    res.igual("F5 riesgo", riesgo, True)
    deficit, ahorro, filas = leer_f6(salidas[6])
    res.igual("F6 déficit", deficit, F6_DEFICIT, TOL_ESTADISTICA)
    for cat, esperado in F6_AHORRO.items():
        res.igual(f"F6 ahorro {cat}", ahorro.get(cat), esperado, TOL_ESTADISTICA)
    res.igual("F6 cantidad de subconjuntos", len(filas), len(F6_SUBCONJUNTOS))
    comparar_tabla(res, "F6", filas, F6_SUBCONJUNTOS, (TOL_ESTADISTICA, 0, 0))
    return res


def main(argv):
    lenguajes = argv or ["python", "scala", "prolog"]
    estado = 0
    for lenguaje in lenguajes:
        salidas = ejecutar(lenguaje)
        if salidas is None:
            print(f"[OMITIDO] {lenguaje}: falta la herramienta (swipl / sbt) en el PATH")
            estado = max(estado, 2)
            continue
        res = verificar(salidas)
        if res.fallos:
            print(f"[FALLA]   {lenguaje}: {len(res.fallos)} de {res.comprobaciones} comprobaciones")
            for fallo in res.fallos:
                print(f"            - {fallo}")
            estado = 1
        else:
            print(f"[OK]      {lenguaje}: {res.comprobaciones} comprobaciones")
    return estado


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
