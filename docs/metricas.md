# Métricas de código

> Generado por `python3 tests/metricas.py`. No editar a mano: vuelve a ejecutar el script.

Líneas de código por funcionalidad y por lenguaje, según la sección 7 de
`datos/especificacion-sistema.md`: sin comentarios, sin líneas en blanco y sin pruebas
(las pruebas están en `tests/`, fuera de los programas medidos).

| Funcionalidad | Python | Scala | Prolog |
|---|---:|---:|---:|
| F1 | 4 | 3 | 6 |
| F2 | 10 | 6 | 11 |
| F3 | 8 | 6 | 8 |
| F4 | 25 | 15 | 21 |
| F5 | 12 | 8 | 26 |
| F6 | 21 | 14 | 34 |
| Menú | 18 | 12 | 17 |
| Compartido | 58 | 24 | 44 |
| **Total (código)** | **156** | **88** | **167** |
| Líneas totales del archivo | 231 | 116 | 227 |
| Suma F1–F6 | 80 | 52 | 106 |

## Cómo se asignan las líneas

El programa se divide en bloques de primer nivel (función, predicado, clase o constante).
Cada bloque se asigna a la funcionalidad que lo usa en exclusiva:

- **Python**: F1 = `f1`; F2 = `f2`; F3 = `f3`; F4 = `estadisticas`, `umbral`, `f4`; F5 = `proyeccion`, `f5`; F6 = `ahorro`, `f6`; Menú = `menu`, `__name__`
- **Scala**: F1 = `f1`; F2 = `f2`; F3 = `f3`; F4 = `stats`, `f4`; F5 = `saldoActual`, `gastoVariable`, `gastoDiario`, `liquidez`, `f5`; F6 = `ahorro`, `f6`; Menú = `menu`, `main`
- **Prolog**: F1 = `f1`; F2 = `micro`, `f2`; F3 = `excedido`, `f3`; F4 = `stats`, `umbral`, `anomalo`, `f4`; F5 = `saldo_actual`, `gasto_variable`, `liquidez`, `riesgo`, `f5`; F6 = `ahorro`, `ahorro_total`, `comb`, `cumple`, `minima`, `f6`; Menú = `opcion`, `menu`, `initialization`

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
