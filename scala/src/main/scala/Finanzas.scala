// Sistema de Gestion Financiera Personal - Scala
import scala.io.Source
import scala.util.Using

case class Gasto(id: Int, mes: Int, dia: Int, cat: String, cent: Int)
case class Ingreso(id: Int, mes: Int, dia: Int, cent: Int)

// Parametros
val archivo = "../datos/movimientos.csv"
val hoyMes = 9; val hoyDia = 20; val diasRestantes = 10
val mesBase = 8
val ventanaIni = 14; val ventanaDias = 7
val microgasto = 1000; val minMicro = 5; val recorte = 0.2
val saldoInicial = 9000; val ingresoEsperado = 10000
val categorias = List("Comida", "Transporte", "Entretenimiento", "Servicios", "Otros")
val catHormiga = List("Comida", "Otros")
val catFija = "Servicios"
val catRecortables = List("Comida", "Transporte", "Entretenimiento", "Otros")
val tope = Map("Comida" -> 20000, "Transporte" -> 8000, "Entretenimiento" -> 12000, "Servicios" -> 20000, "Otros" -> 6000)

// Datos (CSV: id,tipo,mes,dia,categoria,centimos)
val filas = Using.resource(Source.fromFile(archivo, "UTF-8"))(_.getLines().drop(1).map(_.trim).filter(_.nonEmpty).map(_.split(",", -1)).toList)
val gastos = filas.filter(f => f(1) == "GASTO").map(f => Gasto(f(0).toInt, f(2).toInt, f(3).toInt, f(4), f(5).toInt))
val ingresos = filas.filter(f => f(1) == "INGRESO").map(f => Ingreso(f(0).toInt, f(2).toInt, f(3).toInt, f(5).toInt))

// Fechas
def hastaHoy(mes: Int, dia: Int): Boolean = mes < hoyMes || (mes == hoyMes && dia <= hoyDia)
def enVentana(g: Gasto): Boolean = g.mes == hoyMes && g.dia >= ventanaIni && hastaHoy(g.mes, g.dia)

def soles(c: Double): String = f"${c / 100}%.2f"

// F1 Total por categoria
def total(mes: Int, cat: String): Int =
  gastos.filter(g => g.mes == mes && g.cat == cat && hastaHoy(g.mes, g.dia)).map(_.cent).sum

def f1(): Unit =
  println("Categoría        Agosto  Septiembre")
  categorias.foreach(c => println(f"$c%-15s ${soles(total(mesBase, c))}%8s ${soles(total(hoyMes, c))}%11s"))

// F2 Gasto hormiga
def f2(): Unit =
  println("Categoría  Microgastos   Total  ¿Patrón?")
  catHormiga.foreach { c =>
    val micro = gastos.filter(g => enVentana(g) && g.cat == c && g.cent < microgasto).map(_.cent)
    println(f"$c%-9s ${micro.length}%11d ${soles(micro.sum)}%7s  ${if micro.length >= minMicro then "Sí" else "No"}")
  }

// F3 Exceso de presupuesto
def f3(): Unit =
  println("Categoría        Acumulado    Tope  Excedido")
  categorias.foreach { c =>
    val acum = total(hoyMes, c)
    println(f"$c%-15s ${soles(acum)}%10s ${soles(tope(c))}%7s ${soles(math.max(0, acum - tope(c)))}%9s")
  }

// F4 Gastos anomalos
def stats(cat: String): (Int, Double, Double) =
  val x = gastos.filter(g => g.mes == mesBase && g.cat == cat).map(_.cent.toDouble)
  val mu = x.sum / x.length
  (x.length, mu, math.sqrt(x.map(v => (v - mu) * (v - mu)).sum / x.length))

def f4(): Unit =
  println("Categoría        n   Media   Desv.  Umbral")
  categorias.foreach { c =>
    val (n, mu, s) = stats(c)
    println(f"$c%-15s $n%2d ${soles(mu)}%7s ${soles(s)}%7s ${soles(mu + 2 * s)}%7s")
  }
  println("Gastos anómalos:")
  gastos.filter(g => g.mes == hoyMes && hastaHoy(g.mes, g.dia)).foreach { g =>
    val (_, mu, s) = stats(g.cat)
    if g.cent > mu + 2 * s then println(f"  id ${g.id}%d (${g.cat}, S/ ${soles(g.cent)})")
  }

// F5 Liquidez a fin de mes
val saldoActual = saldoInicial + ingresos.filter(i => hastaHoy(i.mes, i.dia)).map(_.cent).sum - gastos.filter(g => hastaHoy(g.mes, g.dia)).map(_.cent).sum
val gastoVariable = gastos.filter(g => enVentana(g) && g.cat != catFija).map(_.cent).sum
val gastoDiario = gastoVariable / ventanaDias.toDouble
val liquidez = saldoActual + ingresoEsperado - gastoDiario * diasRestantes

def f5(): Unit =
  List[(String, Double)]("Saldo actual" -> saldoActual, "Gasto variable de la ventana" -> gastoVariable, "Gasto diario proyectado" -> gastoDiario,
    "Ingreso esperado restante" -> ingresoEsperado, "Liquidez a fin de mes" -> liquidez).foreach((n, v) => println(f"$n%-30s ${soles(v)}%8s"))
  println(s"Riesgo: ${if liquidez < 0 then "sí" else "no"}")

// F6 Plan de ahorro
def ahorro(cat: String): Double =
  gastos.filter(g => enVentana(g) && g.cat == cat).map(_.cent).sum / ventanaDias.toDouble * diasRestantes * recorte

def f6(): Unit =
  if liquidez >= 0 then println("No hay riesgo de liquidez: el plan de ahorro no es necesario")
  else
    val deficit = -liquidez
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
  scala.io.StdIn.readLine() match
    case "1" => f1(); menu()
    case "2" => f2(); menu()
    case "3" => f3(); menu()
    case "4" => f4(); menu()
    case "5" => f5(); menu()
    case "6" => f6(); menu()
    case null | "0" => println("Hasta luego")
    case _ => println("Opción no válida"); menu()

@main def main(): Unit = menu()
