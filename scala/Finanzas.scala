// Sistema de Gestión Financiera Personal - Scala (funcional)
// Montos en céntimos enteros; fechas como (mes, día) enteros.

case class Gasto(id: Int, mes: Int, dia: Int, cat: String, cent: Int)
case class Ingreso(id: Int, mes: Int, dia: Int, cent: Int)

// ---- Datos ----
val gastos = List(
    Gasto(2,8,1,"Comida",980), Gasto(3,8,2,"Comida",920), Gasto(4,8,2,"Transporte",500), Gasto(5,8,3,"Comida",700),
    Gasto(6,8,3,"Otros",1950), Gasto(7,8,4,"Transporte",550), Gasto(8,8,5,"Comida",830), Gasto(9,8,5,"Servicios",3500),
    Gasto(10,8,6,"Comida",1340), Gasto(11,8,7,"Transporte",450), Gasto(12,8,7,"Servicios",8000), Gasto(13,8,8,"Comida",960),
    Gasto(14,8,8,"Entretenimiento",2000), Gasto(15,8,9,"Comida",1250), Gasto(16,8,9,"Otros",650), Gasto(17,8,10,"Transporte",500),
    Gasto(18,8,10,"Servicios",6000), Gasto(19,8,11,"Comida",1080), Gasto(20,8,12,"Comida",1500), Gasto(21,8,13,"Transporte",450),
    Gasto(22,8,13,"Otros",2000), Gasto(23,8,14,"Comida",1060), Gasto(24,8,15,"Transporte",400), Gasto(25,8,15,"Entretenimiento",2500),
    Gasto(26,8,16,"Comida",1100), Gasto(27,8,17,"Comida",1280), Gasto(28,8,18,"Otros",650), Gasto(29,8,19,"Comida",1100),
    Gasto(30,8,20,"Transporte",500), Gasto(32,8,21,"Comida",1390), Gasto(33,8,22,"Entretenimiento",3000), Gasto(34,8,23,"Comida",1350),
    Gasto(35,8,24,"Transporte",500), Gasto(36,8,25,"Comida",1630), Gasto(37,8,26,"Otros",1750), Gasto(38,8,27,"Comida",1410),
    Gasto(39,8,28,"Transporte",400), Gasto(40,8,29,"Comida",1220), Gasto(41,8,29,"Entretenimiento",3500), Gasto(42,8,30,"Otros",850),
    Gasto(43,8,31,"Comida",920), Gasto(45,9,1,"Comida",1400), Gasto(46,9,2,"Servicios",8500), Gasto(47,9,2,"Comida",1350),
    Gasto(48,9,3,"Servicios",6200), Gasto(49,9,3,"Transporte",550), Gasto(50,9,4,"Servicios",3000), Gasto(51,9,4,"Comida",1200),
    Gasto(52,9,5,"Entretenimiento",3500), Gasto(53,9,5,"Otros",2000), Gasto(54,9,6,"Comida",1550), Gasto(55,9,6,"Transporte",450),
    Gasto(56,9,7,"Transporte",2800), Gasto(57,9,7,"Comida",1600), Gasto(58,9,8,"Comida",1300), Gasto(59,9,8,"Entretenimiento",2500),
    Gasto(60,9,9,"Transporte",500), Gasto(61,9,9,"Otros",1400), Gasto(62,9,10,"Comida",1450), Gasto(63,9,10,"Transporte",300),
    Gasto(65,9,13,"Comida",3800), Gasto(66,9,13,"Comida",1300), Gasto(67,9,14,"Comida",750), Gasto(68,9,14,"Transporte",300),
    Gasto(69,9,15,"Comida",850), Gasto(70,9,15,"Otros",650), Gasto(71,9,16,"Comida",900), Gasto(72,9,16,"Transporte",300),
    Gasto(73,9,17,"Comida",650), Gasto(74,9,17,"Otros",500), Gasto(75,9,18,"Comida",800), Gasto(76,9,18,"Transporte",300),
    Gasto(77,9,19,"Comida",950), Gasto(78,9,19,"Entretenimiento",9500), Gasto(79,9,20,"Comida",700), Gasto(80,9,20,"Otros",700)
)
val ingresos = List(Ingreso(1,8,1,55000), Ingreso(31,8,21,10000), Ingreso(44,9,1,55000), Ingreso(64,9,12,10000))

// ---- Parámetros ----
val hoyMes = 9; val hoyDia = 20; val diasRestantes = 10
val ventanaIni = 14; val ventanaDias = 7
val microgasto = 1000; val minMicro = 5
val saldoInicial = 9000; val ingresoEsperado = 10000
val categorias = List("Comida", "Transporte", "Entretenimiento", "Servicios", "Otros")
val tope = Map("Comida" -> 20000, "Transporte" -> 8000, "Entretenimiento" -> 12000, "Servicios" -> 20000, "Otros" -> 6000)

def soles(c: Double): String = f"${c / 100}%.2f"

// ---- Funcionalidades ----
// F1: total de gastos de una categoría en un mes (septiembre solo hasta HOY)
def total(mes: Int, cat: String): Int =
  gastos.filter(g => g.mes == mes && g.cat == cat && (mes < hoyMes || g.dia <= hoyDia)).map(_.cent).sum

def f1(): Unit =
  println("Categoría        Agosto  Septiembre")
  categorias.foreach(c => println(f"$c%-15s ${soles(total(8, c))}%8s ${soles(total(9, c))}%11s"))
// ¿El gasto cae en la ventana de análisis (días 14 al 20)?
def enVentana(g: Gasto): Boolean = g.mes == hoyMes && g.dia >= ventanaIni && g.dia <= hoyDia

// F2: microgastos de la ventana en Comida y Otros
def f2(): Unit =
  println("Categoría  Microgastos   Total  ¿Patrón?")
  List("Comida", "Otros").foreach { c =>
    val micro = gastos.filter(g => enVentana(g) && g.cat == c && g.cent < microgasto).map(_.cent)
    println(f"$c%-9s ${micro.length}%11d ${soles(micro.sum)}%7s  ${if micro.length >= minMicro then "Sí" else "No"}")
  }
// F3: acumulado del mes de corte frente al tope; excedido = max(0, acumulado - tope)
def f3(): Unit =
  println("Categoría        Acumulado    Tope  Excedido")
  categorias.foreach { c =>
    val acum = total(hoyMes, c)
    println(f"$c%-15s ${soles(acum)}%10s ${soles(tope(c))}%7s ${soles(math.max(0, acum - tope(c)))}%9s")
  }
// F4: (n, media, desviación poblacional) de los gastos de agosto de una categoría
def stats(cat: String): (Int, Double, Double) =
  val x = gastos.filter(g => g.mes == 8 && g.cat == cat).map(_.cent.toDouble)
  val mu = x.sum / x.length
  (x.length, mu, math.sqrt(x.map(v => (v - mu) * (v - mu)).sum / x.length))

// Un gasto de septiembre es anómalo si supera media + 2 desviaciones de su categoría
def f4(): Unit =
  println("Categoría        n   Media   Desv.  Umbral")
  categorias.foreach { c =>
    val (n, mu, s) = stats(c)
    println(f"$c%-15s $n%2d ${soles(mu)}%7s ${soles(s)}%7s ${soles(mu + 2 * s)}%7s")
  }
  println("Gastos anómalos:")
  gastos.filter(g => g.mes == hoyMes && g.dia <= hoyDia).foreach { g =>
    val (_, mu, s) = stats(g.cat)
    if g.cent > mu + 2 * s then println(f"  id ${g.id}%d (${g.cat}, S/ ${soles(g.cent)})")
  }
def f5(): Unit = println("F5 pendiente")
def f6(): Unit = println("F6 pendiente")

// ---- Menú ----
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
