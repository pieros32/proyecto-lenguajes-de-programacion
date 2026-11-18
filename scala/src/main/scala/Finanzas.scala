// Sistema de Gestion Financiera Personal - Scala
// Estilo funcional: val inmutables, map/filter/sum sobre listas, sin var. Montos en céntimos enteros
// (evita errores de redondeo con Double); fechas como (mes, día) enteros. Solo se redondea al imprimir.
import scala.io.Source
import scala.util.Using

case class Gasto(id: Int, mes: Int, dia: Int, cat: String, cent: Int)
case class Ingreso(id: Int, mes: Int, dia: Int, cent: Int)

// Parametros (HOY = 20 de septiembre; agosto es la linea base de F4)
val archivo = "../datos/movimientos.csv"
val hoyMes = 9; val hoyDia = 20; val diasRestantes = 10
val mesBase = 8
val ventanaIni = 14; val ventanaDias = 7
val microgasto = 1000; val minMicro = 5; val recorte = 0.2
val saldoInicial = 9000; val ingresoEsperado = 10000
val categorias = List("Comida", "Transporte", "Entretenimiento", "Servicios", "Otros")
val catHormiga = List("Comida", "Otros")
// Servicios es el gasto fijo: ya se pago en el mes, no entra en el gasto diario ni se recorta
val catFija = "Servicios"
val catRecortables = categorias.filter(_ != catFija) // Servicios es gasto fijo: no se recorta
val tope = Map("Comida" -> 20000, "Transporte" -> 8000, "Entretenimiento" -> 12000, "Servicios" -> 20000, "Otros" -> 6000)

// Datos (CSV: id,tipo,mes,dia,categoria,centimos)
val lineas = Using.resource(Source.fromFile(archivo, "UTF-8"))(_.getLines().toList).drop(1)
val filas = lineas.map(_.trim.split(",", -1))
val gastos = filas.collect { case Array(id, "GASTO", mes, dia, cat, cent) => Gasto(id.toInt, mes.toInt, dia.toInt, cat, cent.toInt) }
val ingresos = filas.collect { case Array(id, "INGRESO", mes, dia, _, cent) => Ingreso(id.toInt, mes.toInt, dia.toInt, cent.toInt) }

// Fechas
// Septiembre solo cuenta hasta HOY (dia 20); los meses anteriores cuentan completos.
def hastaHoy(mes: Int, dia: Int): Boolean = mes < hoyMes || (mes == hoyMes && dia <= hoyDia)
// Ventana de analisis: dias 14 al 20 de septiembre (7 dias)
def enVentana(g: Gasto): Boolean = g.mes == hoyMes && g.dia >= ventanaIni && hastaHoy(g.mes, g.dia)

// Los centimos se convierten a soles solo para mostrar
def soles(c: Double): String = f"${c / 100}%.2f"

// F1 Total por categoria
def total(mes: Int, cat: String): Int =
  gastos.filter(g => g.mes == mes && g.cat == cat && hastaHoy(g.mes, g.dia)).map(_.cent).sum

def f1(): Unit =
  println("Categoría        Agosto  Septiembre")
  categorias.foreach(c => println(f"$c%-15s ${soles(total(mesBase, c))}%8s ${soles(total(hoyMes, c))}%11s"))

// F2 Gasto hormiga: microgasto = menos de S/ 10.00 (1000 centimos); patron = 5 o mas en la ventana
def f2(): Unit =
  println("Categoría  Microgastos   Total  ¿Patrón?")
  catHormiga.foreach { c =>
    val micro = gastos.filter(g => enVentana(g) && g.cat == c && g.cent < microgasto).map(_.cent)
    println(f"$c%-9s ${micro.length}%11d ${soles(micro.sum)}%7s  ${if micro.length >= minMicro then "Sí" else "No"}")
  }

// F3 Exceso de presupuesto: excedido = acumulado - tope, con minimo cero (max)
def f3(): Unit =
  println("Categoría        Acumulado    Tope  Excedido")
  categorias.foreach { c =>
    val acum = total(hoyMes, c)
    println(f"$c%-15s ${soles(acum)}%10s ${soles(tope(c))}%7s ${soles(math.max(0, acum - tope(c)))}%9s")
  }

// F4 Gastos anomalos
// (n, media, desviación) de la línea base de agosto. La desviación es poblacional:
// se divide entre n, no entre n - 1, porque agosto completo es toda la población.
def stats(cat: String): (Int, Double, Double) =
  val x = gastos.filter(g => g.mes == mesBase && g.cat == cat).map(_.cent.toDouble)
  val mu = x.sum / x.length
  (x.length, mu, math.sqrt(x.map(v => (v - mu) * (v - mu)).sum / x.length))

// Única definición del umbral de anomalía: media + 2 desviaciones
def umbral(mu: Double, s: Double): Double = mu + 2 * s

def f4(): Unit =
  // Línea base y umbral de cada categoría, calculados una sola vez
  val base = categorias.map(c => c -> stats(c)).toMap
  val umbrales = base.map { case (c, (_, mu, s)) => c -> umbral(mu, s) }
  println("Categoría        n   Media   Desv.  Umbral")
  categorias.foreach { c =>
    val (n, mu, s) = base(c)
    println(f"$c%-15s $n%2d ${soles(mu)}%7s ${soles(s)}%7s ${soles(umbrales(c))}%7s")
  }
  println("Gastos anómalos:")
  gastos.filter(g => g.mes == hoyMes && hastaHoy(g.mes, g.dia) && g.cent > umbrales(g.cat)).foreach { g =>
    println(f"  id ${g.id}%d (${g.cat}, S/ ${soles(g.cent)})")
  }

// F5 Liquidez a fin de mes = saldo actual + ingreso esperado - gasto diario * dias restantes.
// Gasto diario = gasto variable de la ventana / 7; el variable excluye Servicios (gasto fijo).
val saldoActual = saldoInicial + ingresos.filter(i => hastaHoy(i.mes, i.dia)).map(_.cent).sum - gastos.filter(g => hastaHoy(g.mes, g.dia)).map(_.cent).sum
val gastoVariable = gastos.filter(g => enVentana(g) && g.cat != catFija).map(_.cent).sum
val gastoDiario = gastoVariable / ventanaDias.toDouble
val liquidez = saldoActual + ingresoEsperado - gastoDiario * diasRestantes

def f5(): Unit =
  List[(String, Double)]("Saldo actual" -> saldoActual, "Gasto variable de la ventana" -> gastoVariable, "Gasto diario proyectado" -> gastoDiario,
    "Ingreso esperado restante" -> ingresoEsperado, "Liquidez a fin de mes" -> liquidez).foreach((n, v) => println(f"$n%-30s ${soles(v)}%8s"))
  println(s"Riesgo: ${if liquidez < 0 then "sí" else "no"}")

// F6 Plan de ahorro: ahorro(c) = gasto diario de la categoria * dias restantes * 20% de recorte.
// Un grupo de categorias cumple si su ahorro suma al menos el deficit; es minimo si cumple y,
// al quitarle cualquier categoria, deja de cumplir (basta quitar una: los ahorros son >= 0).
def ahorro(cat: String): Double =
  gastos.filter(g => enVentana(g) && g.cat == cat).map(_.cent).sum / ventanaDias.toDouble * diasRestantes * recorte

def f6(): Unit =
  if liquidez >= 0 then println("No hay riesgo de liquidez: el plan de ahorro no es necesario")
  else
    val deficit = -liquidez // liquidez negativa: cuanto falta para llegar a cero
    def cumple(g: List[String]): Boolean = g.map(ahorro).sum >= deficit
    println(s"Déficit: S/ ${soles(deficit)}")
    catRecortables.foreach(c => println(f"$c%-16s ${soles(ahorro(c))}%7s"))
    println("Subconjunto                                    Ahorro  ¿Cumple?  ¿Mínimo?")
    (1 to catRecortables.length).flatMap(catRecortables.combinations).foreach { g =>
      val minimo = cumple(g) && g.forall(c => !cumple(g.filter(_ != c)))
      println(f"${g.mkString(", ")}%-45s ${soles(g.map(ahorro).sum)}%7s  ${if cumple(g) then "Sí" else "No"}%-8s  ${if minimo then "Sí" else "—"}")
    }

// Menu
def menu(): Unit =
  println("\n1) F1 Total por categoría\n2) F2 Gasto hormiga\n3) F3 Exceso de presupuesto\n4) F4 Gastos anómalos\n5) F5 Liquidez a fin de mes\n6) F6 Plan de ahorro\n0) Salir")
  // readLine() devuelve null al fin de entrada: Option lo vuelve None; trim tolera espacios
  Option(scala.io.StdIn.readLine()).map(_.trim) match
    case Some("1") => f1(); menu()
    case Some("2") => f2(); menu()
    case Some("3") => f3(); menu()
    case Some("4") => f4(); menu()
    case Some("5") => f5(); menu()
    case Some("6") => f6(); menu()
    case None | Some("0") => println("Hasta luego")
    case _ => println("Opción no válida"); menu()

@main def main(): Unit = menu()
