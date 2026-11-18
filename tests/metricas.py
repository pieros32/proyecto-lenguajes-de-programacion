"""Mide las líneas de código por funcionalidad y por lenguaje (sección 7 de la especificación)
y escribe docs/metricas.md.

Criterio: solo cuentan las líneas de código. Se excluyen las líneas en blanco, las que solo
tienen comentario (#, //, %, docstrings) y las pruebas (viven en tests/, fuera de los programas).

Cada programa se divide en bloques de primer nivel (una función, un predicado, una clase o una
constante) y cada bloque se asigna a una funcionalidad según las tablas ASIGNACION de abajo.
Lo que no pertenece a una sola funcionalidad (modelo, parámetros, utilidades, helpers
compartidos por varias F) se cuenta aparte como "Compartido".

Uso:  python3 tests/metricas.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "metricas.md"
FUNCIONALIDADES = ["F1", "F2", "F3", "F4", "F5", "F6", "Menú", "Compartido"]

# Bloques de primer nivel que implementan cada funcionalidad. Todo lo no listado es "Compartido".
ASIGNACION = {
    "Python": {
        "F1": ["f1"], "F2": ["f2"], "F3": ["f3"], "F4": ["estadisticas", "umbral", "f4"],
        "F5": ["proyeccion", "f5"], "F6": ["ahorro", "f6"], "Menú": ["menu", "__name__"],
    },
    "Scala": {
        "F1": ["f1"], "F2": ["f2"], "F3": ["f3"], "F4": ["stats", "umbral", "f4"],
        "F5": ["saldoActual", "gastoVariable", "gastoDiario", "liquidez", "f5"],
        "F6": ["ahorro", "f6"], "Menú": ["menu", "main"],
    },
    "Prolog": {
        "F1": ["f1"], "F2": ["micro", "f2"], "F3": ["excedido", "f3"],
        "F4": ["stats", "umbral", "base", "anomalo", "f4"],
        "F5": ["saldo_actual", "gasto_variable", "liquidez", "riesgo", "f5"],
        "F6": ["ahorro", "ahorro_total", "comb", "cumple", "minima", "f6"],
        "Menú": ["opcion", "menu", "initialization"],
    },
}
ARCHIVOS = {
    "Python": RAIZ / "python" / "finanzas.py",
    "Scala": RAIZ / "scala" / "src" / "main" / "scala" / "Finanzas.scala",
    "Prolog": RAIZ / "prolog" / "finanzas.pl",
}
PREFIJO_COMENTARIO = {"Python": "#", "Scala": "//", "Prolog": "%"}


def lineas_de_codigo(lenguaje, texto):
    """Devuelve las líneas con código, sin blancos, comentarios ni docstrings."""
    prefijo = PREFIJO_COMENTARIO[lenguaje]
    codigo, en_docstring = [], False
    for linea in texto.splitlines():
        s = linea.strip()
        if lenguaje == "Python":
            if en_docstring:
                en_docstring = '"""' not in s
                continue
            if s.startswith('"""'):
                en_docstring = s.count('"""') == 1
                continue
        if s and not s.startswith(prefijo):
            codigo.append(linea)
    return codigo


def nombre_de_bloque(lenguaje, linea):
    """Nombre del elemento definido en una línea de primer nivel (None si no define nada)."""
    patron = {
        "Python": r"^(?:def|class)\s+(\w+)|^(\w+)\s*(?:,\s*\w+\s*)*=|^if\s+(__name__)",
        "Scala": r"^(?:@main\s+)?(?:def|val|case class|class)\s+(\w+)",
        "Prolog": r"^([a-z]\w*)|^:-\s*(initialization)",
    }[lenguaje]
    m = re.match(patron, linea)
    return next((g for g in m.groups() if g), None) if m else None


def bloques(lenguaje, lineas):
    """Agrupa las líneas de código en bloques: cada línea sin sangría abre un bloque nuevo
    y las sangradas continúan el anterior. En Prolog se agrupan además las cláusulas del
    mismo predicado."""
    resultado, actual = [], None
    for linea in lineas:
        if not linea[0].isspace():
            nombre = nombre_de_bloque(lenguaje, linea)
            if lenguaje == "Prolog" and nombre and actual and actual["nombre"] == nombre:
                pass  # otra cláusula del mismo predicado
            elif lenguaje == "Prolog" and actual and not nombre_de_bloque(lenguaje, linea) and not linea.startswith(":-"):
                pass  # cierre o continuación sin sangría
            else:
                actual = {"nombre": nombre, "lineas": 0}
                resultado.append(actual)
        if actual is None:
            actual = {"nombre": None, "lineas": 0}
            resultado.append(actual)
        actual["lineas"] += 1
    return resultado


def medir(lenguaje):
    texto = ARCHIVOS[lenguaje].read_text(encoding="utf-8")
    dueno = {n: f for f, nombres in ASIGNACION[lenguaje].items() for n in nombres}
    conteo = {f: 0 for f in FUNCIONALIDADES}
    for b in bloques(lenguaje, lineas_de_codigo(lenguaje, texto)):
        conteo[dueno.get(b["nombre"], "Compartido")] += b["lineas"]
    return conteo, len(texto.splitlines())


def generar():
    medidas = {l: medir(l) for l in ARCHIVOS}
    lenguajes = list(ARCHIVOS)
    filas = ["| Funcionalidad | " + " | ".join(lenguajes) + " |", "|---|" + "---:|" * len(lenguajes)]
    for f in FUNCIONALIDADES:
        filas.append(f"| {f} | " + " | ".join(str(medidas[l][0][f]) for l in lenguajes) + " |")
    filas.append("| **Total (código)** | " + " | ".join(f"**{sum(medidas[l][0].values())}**" for l in lenguajes) + " |")
    filas.append("| Líneas totales del archivo | " + " | ".join(str(medidas[l][1]) for l in lenguajes) + " |")
    solo_f = ["F1", "F2", "F3", "F4", "F5", "F6"]
    filas.append("| Suma F1–F6 | " + " | ".join(str(sum(medidas[l][0][f] for f in solo_f)) for l in lenguajes) + " |")
    return "\n".join(filas), ASIGNACION


def main():
    tabla, asignacion = generar()
    detalle = "\n".join(
        f"- **{l}**: " + "; ".join(f"{f} = {', '.join(f'`{n}`' for n in ns)}" for f, ns in a.items())
        for l, a in asignacion.items())
    texto = f"""# Métricas de código

> Generado por `python3 tests/metricas.py`. No editar a mano: vuelve a ejecutar el script.

Líneas de código por funcionalidad y por lenguaje, según la sección 7 de
`datos/especificacion-sistema.md`: sin comentarios, sin líneas en blanco y sin pruebas
(las pruebas están en `tests/`, fuera de los programas medidos).

{tabla}

## Cómo se asignan las líneas

El programa se divide en bloques de primer nivel (función, predicado, clase o constante).
Cada bloque se asigna a la funcionalidad que lo usa en exclusiva:

{detalle}

**Compartido** agrupa lo que no pertenece a una sola funcionalidad: lectura del CSV y datos,
parámetros, modelo de datos (en Python, las clases `Movimiento`, `Gasto` e `Ingreso`),
utilidades de formato y los helpers que usan varias F (por ejemplo `total`, que sirve a F1 y F3).
**Menú** cuenta aparte el despachador de opciones.

## Cómo leer estas cifras

- Las líneas incluyen el formato de impresión de cada tabla, que en Prolog (`format/2` con
  tabuladores) y en Scala (interpolación `f"..."`) ocupa un peso distinto que en Python.
- El conteo es de líneas físicas, así que depende del estilo de cada autor: una línea larga
  con varias sentencias cuenta una sola vez. Sirve como orden de magnitud, no como medida exacta.
- `Compartido` no es comparable entre lenguajes: en Python incluye las clases del modelo y el
  cargador del CSV, que no tienen equivalente en Scala (dos `case class` de una línea) ni en
  Prolog (los datos son hechos que se cargan con `consult`). Por eso la comparación más justa
  entre paradigmas es la fila de cada F, no el total.
"""
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(texto, encoding="utf-8")
    print(f"Escrito {SALIDA.relative_to(RAIZ)}")
    print(tabla)


if __name__ == "__main__":
    main()
