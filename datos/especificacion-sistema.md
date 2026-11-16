Especificación del sistema — Gestión Financiera Personal

Curso: Lenguajes de Programación (UTP, 2026-II). Mismo sistema en Scala, Prolog y Python. Este documento fija el alcance, las reglas exactas y los resultados esperados. Las tres implementaciones deben producir los mismos resultados con el mismo dataset.

1. Objetivos que cubre
Objetivo 1: detectar patrones de consumo perjudiciales (F2, F3, F4).
Objetivo 2: proyectar la liquidez futura (F5), con una acción correctiva cuando hay riesgo (F6).
2. Modelo de datos
Gasto: id, mes, dia, categoria, centimos.
Ingreso: id, mes, dia, centimos.
Categorías: Comida, Transporte, Entretenimiento, Servicios, Otros.
Montos en céntimos enteros (S/ 8.50 = 850). Los decimales solo aparecen en los cálculos estadísticos (F4, F5, F6).
Fecha como dos enteros (mes, dia), sin tipos de fecha, para que los tres lenguajes calculen igual.
Dataset: movimientos.csv con 80 movimientos (76 gastos y 4 ingresos) entre el 1 de agosto y el 20 de septiembre de 2026. datos.pl contiene los mismos datos como hechos de Prolog.
3. Parámetros
Parámetro	Valor
Fecha de corte (HOY)	mes 9, día 20
Días del mes de corte	30 (días restantes = 10)
Ventana de análisis	7 días: del día 14 al 20
Microgasto	monto menor a S/ 10.00
Categorías sujetas a gasto hormiga	Comida, Otros
Mínimo de microgastos para patrón	5 en la ventana
Umbral de anomalía	media + 2 desviaciones (σ poblacional)
Recorte de ahorro	20%
Saldo inicial (1 de agosto)	S/ 90.00
Ingreso esperado restante del mes	S/ 100.00
Categorías recortables	Comida, Transporte, Entretenimiento, Otros (Servicios es gasto fijo)

Presupuestos mensuales:

Categoría	Tope (S/)
Comida	200.00
Transporte	80.00
Entretenimiento	120.00
Servicios	200.00
Otros	60.00
4. Funcionalidades

F1. Total por categoría. Suma de gastos por mes y categoría.

F2. Gasto hormiga. Para cada categoría sujeta a gasto hormiga, tomar los gastos de la ventana con monto menor al microgasto. Hay patrón si la cantidad es mayor o igual a 5. Se reporta cantidad y total acumulado.

F3. Exceso de presupuesto. Acumulado de la categoría en el mes de corte hasta HOY, comparado con su tope. Se reporta excedido = max(0, acumulado − tope).

F4. Gastos anómalos. Línea base: gastos de agosto de cada categoría, con media μ y desviación estándar poblacional σ (se divide entre n, no entre n−1). Un gasto de septiembre hasta HOY es anómalo si su monto es estrictamente mayor a μ + 2σ.

F5. Liquidez a fin de mes.

saldo_actual   = saldo_inicial + Σ ingresos(≤ HOY) − Σ gastos(≤ HOY)
gasto_diario   = Σ gastos de la ventana, excluyendo Servicios / 7
liquidez_fin   = saldo_actual + ingreso_esperado_restante − gasto_diario × días_restantes
riesgo         = liquidez_fin < 0

Servicios se excluye del gasto diario porque es un gasto fijo que ya se pagó en el mes.

F6. Plan de ahorro. Se ejecuta solo si hay riesgo en F5.

déficit        = −liquidez_fin
ahorro(cat)    = (Σ gastos de cat en la ventana / 7) × días_restantes × 20%
solución       = subconjunto no vacío de categorías recortables con Σ ahorro ≥ déficit
mínima         = solución sin ningún subconjunto propio que también sea solución
5. Resultados esperados

F1. Totales por categoría (S/)

Categoría	Agosto	Septiembre (hasta día 20)
Comida	220.20	205.50
Transporte	42.50	55.00
Entretenimiento	110.00	155.00
Servicios	175.00	177.00
Otros	78.50	52.50

F2. Gasto hormiga (ventana días 14-20)

Categoría	Microgastos	Total (S/)	¿Patrón?
Comida	7	56.00	Sí
Otros	3	18.50	No

F3. Presupuesto (septiembre hasta día 20)

Categoría	Acumulado (S/)	Tope (S/)	Excedido (S/)
Comida	205.50	200.00	5.50
Transporte	55.00	80.00	0.00
Entretenimiento	155.00	120.00	35.00
Servicios	177.00	200.00	0.00
Otros	52.50	60.00	0.00

F4. Anómalos (línea base de agosto)

Categoría	n base	μ (S/)	σ (S/)	Umbral (S/)
Comida	19	11.59	2.38	16.35
Transporte	9	4.72	0.48	5.68
Entretenimiento	4	27.50	5.59	38.68
Servicios	3	58.33	18.41	95.15
Otros	6	13.08	6.00	25.09

Gastos anómalos detectados: id 65 (Comida, S/ 38.00); id 56 (Transporte, S/ 28.00); id 78 (Entretenimiento, S/ 95.00).

F5. Liquidez

Concepto	Valor (S/)
Saldo actual	118.80
Gasto variable de la ventana	178.50
Gasto diario proyectado	25.50
Ingreso esperado restante	100.00
Liquidez a fin de mes	-36.20

Resultado: riesgo = sí.

F6. Plan de ahorro (déficit S/ 36.20)

Categoría recortable	Ahorro con 20% (S/)
Comida	16.00
Transporte	2.57
Entretenimiento	27.14
Otros	5.29
Subconjunto	Ahorro (S/)	¿Cumple?	¿Mínimo?
Comida	16.00	No	—
Transporte	2.57	No	—
Entretenimiento	27.14	No	—
Otros	5.29	No	—
Comida, Transporte	18.57	No	—
Comida, Entretenimiento	43.14	Sí	Sí
Comida, Otros	21.29	No	—
Transporte, Entretenimiento	29.71	No	—
Transporte, Otros	7.86	No	—
Entretenimiento, Otros	32.43	No	—
Comida, Transporte, Entretenimiento	45.71	Sí	—
Comida, Transporte, Otros	23.86	No	—
Comida, Entretenimiento, Otros	48.43	Sí	—
Transporte, Entretenimiento, Otros	35.00	No	—
Comida, Transporte, Entretenimiento, Otros	51.00	Sí	—
6. Reglas de comparabilidad
Los resultados se comparan en céntimos enteros cuando son enteros (F1, F2, F3). En F4, F5 y F6 se aceptan diferencias de ±0.01 soles.
Se redondea solo al imprimir. Los lenguajes redondean distinto, así que no se redondea dentro de los cálculos.
Cada implementación debe producir las tablas de la sección 5 para el mismo dataset.
7. Métricas para el análisis comparativo
Líneas de código por funcionalidad (sin comentarios, líneas en blanco ni pruebas).
Dificultades encontradas (aritmética en Prolog, agrupación, fechas, números decimales).