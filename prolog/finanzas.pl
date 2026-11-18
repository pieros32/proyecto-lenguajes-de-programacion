:- encoding(utf8).

% Sistema de Gestión Financiera Personal - Prolog (SWI-Prolog)
% Montos en céntimos enteros; fechas como (mes, día) enteros.
% Uso:  swipl prolog/finanzas.pl      (menú interactivo)
%       swipl -l prolog/finanzas.pl   (solo carga; luego f1, f2, ... f6)

:- set_stream(user_output, encoding(utf8)).
:- set_stream(user_input, encoding(utf8)).

:- use_module(library(readutil)).
:- use_module(library(lists)).
:- use_module(library(apply)).

% ---- Datos: gasto/5 e ingreso/4 viven en datos/datos.pl ----
:- prolog_load_context(directory, Dir),
   directory_file_path(Dir, '../datos/datos.pl', Ruta),
   consult(Ruta).

% ---- Parámetros ----
hoy(9, 20).
dias_restantes(10).
ventana_ini(14).
ventana_dias(7).
microgasto(1000).
min_micro(5).
recorte(0.2).
saldo_inicial(9000).
ingreso_esperado(10000).

categoria(comida).
categoria(transporte).
categoria(entretenimiento).
categoria(servicios).
categoria(otros).

nombre(comida, 'Comida').
nombre(transporte, 'Transporte').
nombre(entretenimiento, 'Entretenimiento').
nombre(servicios, 'Servicios').
nombre(otros, 'Otros').

tope(comida, 20000).
tope(transporte, 8000).
tope(entretenimiento, 12000).
tope(servicios, 20000).
tope(otros, 6000).

hormiga(comida).
hormiga(otros).

% Servicios es gasto fijo: no se recorta
recortable(C) :- categoria(C), C \== servicios.

% ---- Utilidades ----
soles(Cent, Texto) :- V is Cent / 100, format(atom(Texto), '~2f', [V]).

sino(true, 'Sí').
sino(false, 'No').

% ¿(Mes, Dia) es anterior o igual a HOY?
hasta_hoy(M, D) :- hoy(HM, HD), ( M < HM -> true ; M =:= HM, D =< HD ).

% ¿El gasto cae en la ventana de análisis (días 14 al 20 del mes de corte)?
en_ventana(M, D) :- hoy(HM, HD), ventana_ini(I), M =:= HM, D >= I, D =< HD.

% ---- F1: total de gastos de una categoría en un mes (hasta HOY) ----
total(Mes, Cat, T) :-
    findall(C, (gasto(_, Mes, D, Cat, C), hasta_hoy(Mes, D)), L),
    sum_list(L, T).

f1 :-
    format('~w~t~16|~t~w~8+~t~w~12+~n', ['Categoría', 'Agosto', 'Septiembre']),
    forall(categoria(Cat),
           ( total(8, Cat, A), total(9, Cat, S),
             nombre(Cat, N), soles(A, TA), soles(S, TS),
             format('~w~t~16|~t~w~8+~t~w~12+~n', [N, TA, TS]) )).

% ---- F2: microgastos de la ventana en categorías sujetas a gasto hormiga ----
micro(Cat, Cents) :-
    microgasto(Lim),
    findall(C, (gasto(_, M, D, Cat, C), en_ventana(M, D), C < Lim), Cents).

f2 :-
    format('~w~t~12|~t~w~12+~t~w~9+~t~w~10+~n', ['Categoría', 'Microgastos', 'Total', '¿Patrón?']),
    min_micro(Min),
    forall(( categoria(Cat), hormiga(Cat) ),
           ( micro(Cat, L), length(L, N), sum_list(L, T),
             ( N >= Min -> P = true ; P = false ),
             nombre(Cat, Nom), soles(T, TS), sino(P, PS),
             format('~w~t~12|~t~d~12+~t~w~9+~t~w~10+~n', [Nom, N, TS, PS]) )).

% ---- F3: acumulado del mes de corte frente al tope ----
excedido(Acum, Tope, E) :- E is max(0, Acum - Tope).

f3 :-
    hoy(HM, _),
    format('~w~t~16|~t~w~10+~t~w~9+~t~w~10+~n', ['Categoría', 'Acumulado', 'Tope', 'Excedido']),
    forall(categoria(Cat),
           ( total(HM, Cat, A), tope(Cat, T), excedido(A, T, E),
             nombre(Cat, N), soles(A, SA), soles(T, ST), soles(E, SE),
             format('~w~t~16|~t~w~10+~t~w~9+~t~w~10+~n', [N, SA, ST, SE]) )).

% ---- F4: línea base de agosto (n, media, σ poblacional) y gastos anómalos ----
stats(Cat, N, Mu, Sigma) :-
    findall(C, gasto(_, 8, _, Cat, C), L),
    length(L, N), N > 0,
    sum_list(L, S), Mu is S / N,
    foldl([X, A0, A]>>(A is A0 + (X - Mu) ** 2), L, 0, SumSq),
    Sigma is sqrt(SumSq / N).

% Única definición del umbral: media + 2 desviaciones
umbral(Mu, Sigma, U) :- U is Mu + 2 * Sigma.

% Línea base de una categoría, calculada una sola vez por f4
base(b(Cat, N, Mu, Sg, U)) :-
    categoria(Cat), stats(Cat, N, Mu, Sg), umbral(Mu, Sg, U).

% Gasto de septiembre (hasta HOY) estrictamente mayor al umbral de su categoría
anomalo(Bases, Id, Cat, C) :-
    hoy(HM, HD),
    gasto(Id, HM, D, Cat, C), D =< HD,
    memberchk(b(Cat, _, _, _, U), Bases), C > U.

f4 :-
    format('~w~t~16|~t~w~4+~t~w~9+~t~w~9+~t~w~9+~n', ['Categoría', 'n', 'Media', 'Desv.', 'Umbral']),
    findall(B, base(B), Bases),
    forall(member(b(Cat, N, Mu, Sg, U), Bases),
           ( nombre(Cat, Nom), soles(Mu, SM), soles(Sg, SS), soles(U, SU),
             format('~w~t~16|~t~d~4+~t~w~9+~t~w~9+~t~w~9+~n', [Nom, N, SM, SS, SU]) )),
    writeln('Gastos anómalos:'),
    forall(anomalo(Bases, Id, Cat, C),
           ( nombre(Cat, Nom), soles(C, SC),
             format('  id ~d (~w, S/ ~w)~n', [Id, Nom, SC]) )).

% ---- F5: proyección de liquidez (céntimos sin redondear) ----
saldo_actual(S) :-
    saldo_inicial(S0),
    findall(C, (ingreso(_, M, D, C), hasta_hoy(M, D)), Is), sum_list(Is, TI),
    findall(C, (gasto(_, M, D, _, C), hasta_hoy(M, D)), Gs), sum_list(Gs, TG),
    S is S0 + TI - TG.

% Gasto de la ventana sin Servicios (gasto fijo ya pagado en el mes)
gasto_variable(V) :-
    findall(C, (gasto(_, M, D, Cat, C), en_ventana(M, D), Cat \== servicios), L),
    sum_list(L, V).

liquidez(Saldo, Variable, Diario, Liq) :-
    saldo_actual(Saldo),
    gasto_variable(Variable),
    ventana_dias(W), Diario is Variable / W,
    ingreso_esperado(IE), dias_restantes(DR),
    Liq is Saldo + IE - Diario * DR.

riesgo :- liquidez(_, _, _, L), L < 0.

f5 :-
    liquidez(Saldo, Var, Diario, Liq),
    ingreso_esperado(IE),
    forall(member(Nom-V, [ 'Saldo actual'-Saldo,
                           'Gasto variable de la ventana'-Var,
                           'Gasto diario proyectado'-Diario,
                           'Ingreso esperado restante'-IE,
                           'Liquidez a fin de mes'-Liq ]),
           ( soles(V, S), format('~w~t~30|~t~w~8+~n', [Nom, S]) )),
    ( riesgo -> R = 'sí' ; R = 'no' ),
    format('Riesgo: ~w~n', [R]).

% ---- F6: plan de ahorro, solo si F5 detecta riesgo ----
% ahorro(Cat) = (gastos de Cat en la ventana / 7) * días_restantes * 20%
ahorro(Cat, A) :-
    findall(C, (gasto(_, M, D, Cat, C), en_ventana(M, D)), L),
    sum_list(L, S),
    ventana_dias(W), dias_restantes(DR), recorte(R),
    A is S / W * DR * R.

ahorro_total(Cats, A) :-
    foldl([C, A0, A1]>>(ahorro(C, X), A1 is A0 + X), Cats, 0, A).

% comb(K, Lista, Sub): subconjuntos de tamaño K conservando el orden
comb(0, _, []) :- !.
comb(K, [X|Xs], [X|Ys]) :- K > 0, K1 is K - 1, comb(K1, Xs, Ys).
comb(K, [_|Xs], Ys) :- K > 0, comb(K, Xs, Ys).

cumple(Deficit, Sub) :- ahorro_total(Sub, A), A >= Deficit.

% Mínima: cumple y ningún subconjunto propio no vacío cumple
minima(Deficit, Sub) :-
    cumple(Deficit, Sub),
    length(Sub, K),
    \+ ( K1 is K - 1, between(1, K1, K2), comb(K2, Sub, T), cumple(Deficit, T) ).

f6 :-
    liquidez(_, _, _, Liq),
    (   Liq >= 0
    ->  writeln('No hay riesgo de liquidez: el plan de ahorro no es necesario')
    ;   Deficit is -Liq,
        soles(Deficit, SD), format('Déficit: S/ ~w~n', [SD]),
        findall(C, recortable(C), Rec),
        forall(member(C, Rec),
               ( ahorro(C, A), nombre(C, N), soles(A, SA),
                 format('~w~t~16|~t~w~8+~n', [N, SA]) )),
        format('~w~t~46|~t~w~8+~t~w~10+~t~w~10+~n', ['Subconjunto', 'Ahorro', '¿Cumple?', '¿Mínimo?']),
        length(Rec, Max),
        forall(( between(1, Max, K), comb(K, Rec, Sub) ),
               ( ahorro_total(Sub, A), soles(A, SA),
                 maplist(nombre, Sub, Noms), atomic_list_concat(Noms, ', ', Txt),
                 ( cumple(Deficit, Sub) -> Cu = 'Sí' ; Cu = 'No' ),
                 ( minima(Deficit, Sub) -> Mi = 'Sí' ; Mi = '—' ),
                 format('~w~t~46|~t~w~8+~t~w~10+~t~w~10+~n', [Txt, SA, Cu, Mi]) ))
    ).

% ---- Menú ----
opcion("1", f1).
opcion("2", f2).
opcion("3", f3).
opcion("4", f4).
opcion("5", f5).
opcion("6", f6).

menu :-
    format('~n1) F1 Total por categoría~n2) F2 Gasto hormiga~n3) F3 Exceso de presupuesto~n'),
    format('4) F4 Gastos anómalos~n5) F5 Liquidez a fin de mes~n6) F6 Plan de ahorro~n0) Salir~n'),
    read_line_to_string(user_input, Linea),
    (   ( Linea == end_of_file ; normalize_space(string("0"), Linea) )
    ->  writeln('Hasta luego')
    ;   normalize_space(string(Op), Linea),
        (   opcion(Op, Meta) -> call(Meta) ; writeln('Opción no válida') ),
        menu
    ).

:- initialization(menu, main).
