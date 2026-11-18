name := "gestion-financiera"
scalaVersion := "3.10.1"
// Fija el punto de entrada para que "sbt run" no pregunte cuál ejecutar
Compile / mainClass := Some("main")
// El menú lee de la consola: la ejecución debe usar la misma consola del IDE o terminal
run / fork := true
run / connectInput := true
// Las tildes salen bien en la consola
run / javaOptions += "-Dstdout.encoding=UTF-8"
