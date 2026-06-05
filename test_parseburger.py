# ============================================================
#  ParseBurger — Suite de Pruebas Completa
#  Corre con:  python test_parseburger.py
#
#  Módulos cubiertos:
#    1. Tokenizador
#    2. Parser CFG
#    3. DCG (concordancia + unificación)
#    4. Ambigüedad + PCFG
#    5. ATN Mesero (flujos completos)
# ============================================================

import sys
import traceback

# ── Colores para la terminal ──────────────────────────────────
VERDE  = "\033[92m"
ROJO   = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRIS   = "\033[90m"

# ── Contadores globales ───────────────────────────────────────
total_ok  = 0
total_fail = 0
fallos     = []   # guarda (módulo, nombre, esperado, obtenido)

def ok(modulo, nombre):
    global total_ok
    total_ok += 1
    print(f"  {VERDE}✓{RESET} {nombre}")

def fail(modulo, nombre, esperado, obtenido):
    global total_fail
    total_fail += 1
    fallos.append((modulo, nombre, esperado, obtenido))
    print(f"  {ROJO}✗{RESET} {nombre}")
    print(f"    {GRIS}esperado : {esperado}{RESET}")
    print(f"    {GRIS}obtenido : {obtenido}{RESET}")

def seccion(titulo):
    print(f"\n{BOLD}{CYAN}{'═'*55}{RESET}")
    print(f"{BOLD}{CYAN}  {titulo}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*55}{RESET}")

def subseccion(titulo):
    print(f"\n  {BOLD}── {titulo} ──{RESET}")

def assert_igual(modulo, nombre, esperado, obtenido):
    if esperado == obtenido:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, esperado, obtenido)

def assert_verdadero(modulo, nombre, condicion, detalle=""):
    if condicion:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, "True", f"False  {detalle}")

def assert_nulo(modulo, nombre, valor):
    if valor is None:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, None, valor)

def assert_no_nulo(modulo, nombre, valor):
    if valor is not None:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, "valor no None", None)

# ══════════════════════════════════════════════════════════════
#  1. TOKENIZADOR
# ══════════════════════════════════════════════════════════════

def test_tokenizador():
    seccion("1. TOKENIZADOR")
    from tokenizador import tokenizar
    MOD = "Tokenizador"

    subseccion("Normalización básica")
    assert_igual(MOD, "minúsculas",
        ["quiero", "una", "clasica"],
        tokenizar("QUIERO UNA CLASICA"))

    assert_igual(MOD, "elimina puntuación",
        ["quiero", "una", "clasica"],
        tokenizar("quiero, una clásica."))

    assert_igual(MOD, "elimina tildes (á→a, é→e, í→i, ó→o, ú→u)",
        ["quiero", "una", "clasica"],
        tokenizar("quiero una clásica"))

    subseccion("Palabras ignoradas")
    assert_igual(MOD, "ignora 'por'",
        ["quiero", "una", "clasica"],
        tokenizar("por quiero una clasica"))

    assert_igual(MOD, "ignora 'favor'",
        ["quiero", "una", "clasica"],
        tokenizar("quiero una clasica favor"))

    assert_igual(MOD, "ignora 'me'",
        ["dame", "una", "clasica"],
        tokenizar("me dame una clasica"))

    assert_igual(MOD, "ignora 'pedir'",
        ["quiero", "una", "clasica"],
        tokenizar("pedir quiero una clasica"))

    subseccion("Frases multi-palabra")
    assert_igual(MOD, "perro caliente → perro_caliente",
        ["quiero", "un", "perro_caliente"],
        tokenizar("quiero un perro caliente"))

    assert_igual(MOD, "perro-caliente → perro_caliente",
        ["quiero", "un", "perro_caliente"],
        tokenizar("quiero un perro-caliente"))

    assert_igual(MOD, "hot dog → hotdog",
        ["quiero", "un", "hotdog"],
        tokenizar("quiero un hot dog"))

    assert_igual(MOD, "hot-dog → hotdog",
        ["quiero", "un", "hotdog"],
        tokenizar("quiero un hot-dog"))

    subseccion("Casos completos")
    assert_igual(MOD, "pedido completo con modificadores",
        ["quiero", "dos", "hamburguesas", "sin", "cebolla", "con", "queso"],
        tokenizar("quiero dos hamburguesas sin cebolla con queso"))

    assert_igual(MOD, "entrada con coma y tilde",
        ["dame", "una", "clasica", "sin", "cebolla"],
        tokenizar("Dame, una Clásica sin cebolla."))

    assert_igual(MOD, "tokeniza 'pero' (no ignorado)",
        ["quiero", "una", "clasica", "pero", "sin", "cebolla"],
        tokenizar("quiero una clasica pero sin cebolla"))

    assert_igual(MOD, "tokeniza 'y' (no ignorado)",
        ["quiero", "una", "clasica", "sin", "tomate", "y", "lechuga"],
        tokenizar("quiero una clasica sin tomate y lechuga"))


# ══════════════════════════════════════════════════════════════
#  2. PARSER CFG
# ══════════════════════════════════════════════════════════════

def test_parser_cfg():
    seccion("2. PARSER CFG")
    from tokenizador import tokenizar
    from gramatica   import grammar
    from parser      import parse, parse_todos
    MOD = "Parser CFG"

    def acepta_s(entrada):
        tokens = tokenizar(entrada)
        todos  = parse_todos("S", tokens, 0, grammar)
        return [(n, p) for n, p in todos if p == len(tokens)]

    def acepta_pedido(entrada):
        tokens = tokenizar(entrada)
        todos  = parse_todos("PEDIDO", tokens, 0, grammar)
        return [(n, p) for n, p in todos if p == len(tokens)]

    subseccion("Pedidos válidos — deben aceptarse")
    assert_verdadero(MOD, "un doble",
        len(acepta_pedido("dame un doble")) >= 1)

    assert_verdadero(MOD, "una clasica",
        len(acepta_pedido("quiero una clasica")) >= 1)

    assert_verdadero(MOD, "dos hamburguesas",
        len(acepta_pedido("quiero dos hamburguesas")) >= 1)

    assert_verdadero(MOD, "tres hamburguesas con queso",
        len(acepta_pedido("quisiera tres hamburguesas con queso")) >= 1)

    assert_verdadero(MOD, "pedido con extra: con extra tocino",
        len(acepta_pedido("ponme una especial con extra tocino")) >= 1)

    assert_verdadero(MOD, "pedido con pero: sin cebolla pero con queso",
        len(acepta_pedido("quiero una clasica sin cebolla pero con queso")) >= 1)

    assert_verdadero(MOD, "pedido con salsa (FIX Error 1)",
        len(acepta_pedido("quiero una clasica con salsa")) >= 1)

    assert_verdadero(MOD, "hamburguesa + adjetivo: hamburguesa clasica",
        len(acepta_pedido("quiero una hamburguesa clasica")) >= 1)

    assert_verdadero(MOD, "lista de pedidos: una clasica y una vegana",
        len(acepta_pedido("quiero una clasica y una vegana")) >= 1)

    subseccion("Entradas inválidas — deben rechazarse como PEDIDO")
    # La CFG sí las acepta bajo ENTRADA_INVALIDA, no bajo PEDIDO
    assert_igual(MOD, "perro_caliente → no es PEDIDO válido",
        0, len(acepta_pedido("quiero un perro_caliente")))

    assert_igual(MOD, "pizza → no es PEDIDO válido",
        0, len(acepta_pedido("quiero una pizza")))

    subseccion("Entradas inválidas — detectadas por ENTRADA_INVALIDA")
    def es_invalida(entrada):
        tokens = tokenizar(entrada)
        arbol, pos = parse("ENTRADA_INVALIDA", tokens, 0, grammar)
        return arbol is not None and pos == len(tokens)

    assert_verdadero(MOD, "perro_caliente → ENTRADA_INVALIDA",
        es_invalida("quiero un perro_caliente"))

    assert_verdadero(MOD, "pizza → ENTRADA_INVALIDA",
        es_invalida("dame una pizza"))

    assert_verdadero(MOD, "hotdog → ENTRADA_INVALIDA",
        es_invalida("quiero un hotdog"))

    subseccion("Árbol de derivación — estructura correcta")
    tokens = tokenizar("quiero una clasica")
    arbol, pos = parse("PEDIDO", tokens, 0, grammar)
    assert_verdadero(MOD, "árbol no es None para pedido simple",
        arbol is not None)
    assert_igual(MOD, "consume todos los tokens",
        len(tokens), pos)
    assert_igual(MOD, "raíz del árbol es PEDIDO",
        "PEDIDO", arbol.etiqueta)
    assert_igual(MOD, "primer hijo es VERBO_PEDIR",
        "VERBO_PEDIR", arbol.hijos[0].etiqueta)


# ══════════════════════════════════════════════════════════════
#  3. DCG — UNIFICACIÓN Y CONCORDANCIA
# ══════════════════════════════════════════════════════════════

def test_dcg():
    seccion("3. DCG — UNIFICACIÓN Y CONCORDANCIA")
    from lexico import unificar, dcg_parse_pedido, dcg_parse_lista_pedidos
    from tokenizador import tokenizar
    MOD = "DCG"

    subseccion("unificar() — casos base")
    assert_igual(MOD, "unificar iguales: {num:sg} + {num:sg}",
        {"num": "sg"},
        unificar({"num": "sg"}, {"num": "sg"}))

    assert_nulo(MOD, "conflicto: {num:sg} + {num:pl} → None",
        unificar({"num": "sg"}, {"num": "pl"}))

    assert_igual(MOD, "merge sin conflicto: {a:1} + {b:2}",
        {"a": 1, "b": 2},
        unificar({"a": 1}, {"b": 2}))

    assert_igual(MOD, "merge con clave compartida igual",
        {"cat": "N", "num": "sg"},
        unificar({"cat": "N", "num": "sg"}, {"num": "sg"}))

    assert_nulo(MOD, "conflicto en clave compartida → None",
        unificar({"cat": "N"}, {"cat": "V"}))

    subseccion("dcg_parse_pedido() — concordancia correcta")
    def dcg_ok(entrada):
        return dcg_parse_pedido(tokenizar(entrada))

    r = dcg_ok("quiero dos hamburguesas")
    assert_no_nulo(MOD, "dos hamburguesas → OK", r)
    if r:
        assert_igual(MOD, "  producto detectado: 'hamburguesas'",
            "hamburguesas", r["producto"])
        assert_igual(MOD, "  sin modificadores",
            [], r["modificadores"])

    r = dcg_ok("dame una clasica")
    assert_no_nulo(MOD, "una clasica → OK", r)

    r = dcg_ok("quiero una clasica con queso sin cebolla")
    assert_no_nulo(MOD, "una clasica con queso sin cebolla → OK", r)
    if r:
        mods = r["modificadores"]
        assert_igual(MOD, "  2 modificadores",     2, len(mods))
        assert_igual(MOD, "  1er mod: +queso",     {"tipo": "POS", "ing": "queso"}, mods[0])
        assert_igual(MOD, "  2do mod: -cebolla",   {"tipo": "NEG", "ing": "cebolla"}, mods[1])

    r = dcg_ok("ponme una especial con extra tocino")
    assert_no_nulo(MOD, "una especial con extra tocino → OK", r)
    if r:
        assert_igual(MOD, "  mod EXTRA",
            {"tipo": "EXTRA", "ing": "tocino"}, r["modificadores"][0])

    r = dcg_ok("quiero una clasica con salsa")
    assert_no_nulo(MOD, "con salsa → OK (FIX Error 1)", r)

    subseccion("dcg_parse_pedido() — errores de concordancia")
    assert_nulo(MOD, "FALLA: 'un hamburguesas' (sg + pl)",
        dcg_ok("quiero un hamburguesas"))

    assert_nulo(MOD, "FALLA: 'una doble' (fem + masc)",
        dcg_ok("dame una doble"))

    assert_nulo(MOD, "FALLA: 'un vegana' (masc + fem)",
        dcg_ok("quiero un vegana"))

    subseccion("dcg_parse_lista_pedidos() — múltiples productos")
    def lista_ok(entrada):
        return dcg_parse_lista_pedidos(tokenizar(entrada))

    r = lista_ok("quiero una clasica y una vegana")
    assert_no_nulo(MOD, "lista: una clasica y una vegana → OK", r)
    if r:
        assert_igual(MOD, "  2 sub-pedidos",   2, len(r))
        assert_igual(MOD, "  1er producto: clasica",  "clasica", r[0]["producto"])
        assert_igual(MOD, "  2do producto: vegana",   "vegana",  r[1]["producto"])

    r = lista_ok("dame dos hamburguesas sin cebolla")
    assert_no_nulo(MOD, "lista simple → OK", r)

    assert_nulo(MOD, "lista FALLA: 'un hamburguesas' (concordancia)",
        lista_ok("quiero un hamburguesas"))

    assert_nulo(MOD, "lista FALLA: 'una doble'",
        lista_ok("dame una doble"))


# ══════════════════════════════════════════════════════════════
#  4. AMBIGÜEDAD + PCFG
# ══════════════════════════════════════════════════════════════

def test_ambiguedad_pcfg():
    seccion("4. AMBIGÜEDAD + PCFG")
    from tokenizador import tokenizar
    from ambiguedad  import detectar_ambiguedad, pcfg_score, mejor_arbol_pcfg, PCFG_PROBS
    from gramatica   import grammar
    from parser      import parse_todos, Nodo
    MOD = "Ambigüedad+PCFG"

    subseccion("detectar_ambiguedad() — patrones ambiguos")
    def ambiguo(entrada):
        return detectar_ambiguedad(tokenizar(entrada))

    patron, args = ambiguo("dame una clasica sin tomate y lechuga")
    assert_no_nulo(MOD, "detecta 'sin X y Y' como ambiguo", patron)
    assert_igual(MOD, "  args correctos: [tomate, lechuga]",
        ["tomate", "lechuga"], args)

    patron, args = ambiguo("quiero una vegana sin queso y cebolla")
    assert_no_nulo(MOD, "detecta 'sin queso y cebolla'", patron)
    assert_igual(MOD, "  args: [queso, cebolla]", ["queso", "cebolla"], args)

    subseccion("detectar_ambiguedad() — casos NO ambiguos")
    patron, args = ambiguo("quiero una clasica sin cebolla con queso")
    assert_nulo(MOD, "sin cebolla CON queso → no ambiguo", patron)

    patron, args = ambiguo("dame dos hamburguesas")
    assert_nulo(MOD, "sin modificadores → no ambiguo", patron)

    patron, args = ambiguo("quiero una clasica sin tomate")
    assert_nulo(MOD, "un solo ingrediente negado → no ambiguo", patron)

    subseccion("Interpretaciones del patrón ambiguo")
    patron, args = ambiguo("dame una clasica sin tomate y lechuga")
    if patron:
        interp_a = patron["interpretaciones"][0](*args)
        interp_b = patron["interpretaciones"][1](*args)
        assert_igual(MOD, "Interp A: ambos negativos",
            [{"tipo": "NEG", "ing": "tomate"}, {"tipo": "NEG", "ing": "lechuga"}],
            interp_a)
        assert_igual(MOD, "Interp B: primero neg, segundo pos",
            [{"tipo": "NEG", "ing": "tomate"}, {"tipo": "POS", "ing": "lechuga"}],
            interp_b)

    subseccion("PCFG_PROBS — consistencia con gramática real (FIX Error 2)")
    # Verificar que las producciones obsoletas ya no están
    mol_list_probs = PCFG_PROBS.get("MOD_LIST", {})
    claves = list(mol_list_probs.keys())

    assert_verdadero(MOD, "MOD_LIST contiene ('MOD', 'MOD_LIST_TAIL')",
        ("MOD", "MOD_LIST_TAIL") in mol_list_probs)

    assert_verdadero(MOD, "MOD_LIST contiene ('MOD',)",
        ("MOD",) in mol_list_probs)

    assert_verdadero(MOD, "MOD_LIST NO tiene producción obsoleta ('MOD_LIST','CONJ','MOD')",
        ("MOD_LIST", "CONJ", "MOD") not in mol_list_probs)

    assert_verdadero(MOD, "MOD_LIST NO tiene producción obsoleta ('MOD_LIST','pero','MOD')",
        ("MOD_LIST", "pero", "MOD") not in mol_list_probs)

    assert_verdadero(MOD, "PCFG_PROBS incluye tabla para MOD_LIST_TAIL",
        "MOD_LIST_TAIL" in PCFG_PROBS)

    subseccion("pcfg_score() — valores razonables")
    tokens = tokenizar("quiero dos hamburguesas sin cebolla con queso")
    todos  = parse_todos("PEDIDO", tokens, 0, grammar)
    valid  = [(n, p) for n, p in todos if p == len(tokens)]
    assert_verdadero(MOD, "hay al menos 1 árbol para el pedido",
        len(valid) >= 1)
    if valid:
        score = pcfg_score(valid[0][0])
        assert_verdadero(MOD, f"score > 0 (obtenido: {score:.6f})",
            score > 0)
        assert_verdadero(MOD, f"score <= 1 (obtenido: {score:.6f})",
            score <= 1.0)

    subseccion("mejor_arbol_pcfg()")
    assert_nulo(MOD, "mejor_arbol_pcfg([]) → None",
        mejor_arbol_pcfg([]))

    if valid:
        mejor = mejor_arbol_pcfg(valid)
        assert_no_nulo(MOD, "mejor_arbol_pcfg con 1 árbol → no None", mejor)


# ══════════════════════════════════════════════════════════════
#  5. ATN MESERO — FLUJOS COMPLETOS
# ══════════════════════════════════════════════════════════════

def test_atn():
    seccion("5. ATN MESERO — FLUJOS DE DIÁLOGO")
    from atn_mesero import ATNMesero
    MOD = "ATN"

    def nuevo_mesero():
        m = ATNMesero()
        m.transicion("inicio")   # INICIO → ESCUCHANDO
        return m

    subseccion("Estado inicial y transición de bienvenida")
    m = ATNMesero()
    assert_igual(MOD, "estado inicial es INICIO", "INICIO", m.estado)
    resp = m.transicion("inicio")
    assert_igual(MOD, "transición a ESCUCHANDO", "ESCUCHANDO", m.estado)
    assert_verdadero(MOD, "bienvenida contiene menú",
        "ParseBurger" in resp)

    subseccion("Flujo 1 — pedido válido → confirmar → FIN")
    m = nuevo_mesero()
    resp = m.transicion("quiero dos hamburguesas sin cebolla")
    assert_igual(MOD, "  F1: pasa a CONFIRMANDO", "CONFIRMANDO", m.estado)
    assert_verdadero(MOD, "  F1: respuesta contiene 'hamburguesas'",
        "hamburguesas" in resp.lower())
    resp = m.transicion("si")
    assert_igual(MOD, "  F1: confirmar → FIN", "FIN", m.estado)
    assert_verdadero(MOD, "  F1: respuesta contiene confirmación",
        "confirmado" in resp.lower() or "✅" in resp)

    subseccion("Flujo 2 — pedido válido → cancelar → vuelve a ESCUCHANDO")
    m = nuevo_mesero()
    m.transicion("dame una clasica con queso")
    assert_igual(MOD, "  F2: en CONFIRMANDO", "CONFIRMANDO", m.estado)
    resp = m.transicion("no")
    assert_igual(MOD, "  F2: cancelar → ESCUCHANDO", "ESCUCHANDO", m.estado)
    assert_verdadero(MOD, "  F2: respuesta menciona cancelación",
        "cancelad" in resp.lower())

    subseccion("Flujo 3 — ambigüedad, elige A")
    m = nuevo_mesero()
    resp = m.transicion("dame una clasica sin tomate y lechuga")
    assert_igual(MOD, "  F3: pasa a AMBIGUO", "AMBIGUO", m.estado)
    assert_verdadero(MOD, "  F3: pregunta A o B",
        "(A)" in resp and "(B)" in resp)
    m.transicion("a")
    assert_igual(MOD, "  F3: resolución A → CONFIRMANDO", "CONFIRMANDO", m.estado)
    m.transicion("si")
    assert_igual(MOD, "  F3: confirmar → FIN", "FIN", m.estado)

    subseccion("Flujo 4 — ambigüedad, elige B")
    m = nuevo_mesero()
    m.transicion("dame una clasica sin tomate y lechuga")
    m.transicion("b")
    assert_igual(MOD, "  F4: resolución B → CONFIRMANDO", "CONFIRMANDO", m.estado)

    subseccion("Flujo 5 — ambigüedad, respuesta inválida (bucle)")
    m = nuevo_mesero()
    m.transicion("dame una clasica sin tomate y lechuga")
    resp = m.transicion("si")    # respuesta inválida en estado AMBIGUO
    assert_igual(MOD, "  F5: respuesta inválida → sigue en AMBIGUO", "AMBIGUO", m.estado)
    assert_verdadero(MOD, "  F5: respuesta pide A o B",
        "A" in resp and "B" in resp)

    subseccion("Flujo 6 — entrada inválida (fuera del menú)")
    m = nuevo_mesero()
    resp = m.transicion("quiero un perro_caliente")
    assert_igual(MOD, "  F6: entrada inválida → sigue en ESCUCHANDO", "ESCUCHANDO", m.estado)
    assert_verdadero(MOD, "  F6: respuesta menciona menú",
        "men" in resp.lower())

    subseccion("Flujo 7 — error de concordancia")
    m = nuevo_mesero()
    resp = m.transicion("quiero un hamburguesas")
    assert_igual(MOD, "  F7: concordancia falla → sigue en ESCUCHANDO", "ESCUCHANDO", m.estado)
    assert_verdadero(MOD, "  F7: respuesta menciona concordancia",
        "concordancia" in resp.lower() or "reformula" in resp.lower())

    subseccion("Flujo 8 — pedido no reconocido")
    m = nuevo_mesero()
    resp = m.transicion("hola como estas")
    assert_igual(MOD, "  F8: no reconocido → sigue en ESCUCHANDO", "ESCUCHANDO", m.estado)
    assert_verdadero(MOD, "  F8: pide reformulación",
        "interpret" in resp.lower() or "forma" in resp.lower())

    subseccion("Flujo 9 — estado FIN no procesa más pedidos")
    m = nuevo_mesero()
    m.transicion("quiero una clasica")
    m.transicion("si")
    assert_igual(MOD, "  F9: en FIN", "FIN", m.estado)
    resp = m.transicion("quiero otra hamburguesa")
    assert_igual(MOD, "  F9: FIN → sigue en FIN", "FIN", m.estado)
    assert_verdadero(MOD, "  F9: respuesta indica cierre",
        "procesado" in resp.lower() or "pronto" in resp.lower())

    subseccion("Flujo 10 — pedido con salsa (FIX Error 1)")
    m = nuevo_mesero()
    resp = m.transicion("quiero una clasica con salsa")
    assert_igual(MOD, "  F10: salsa aceptada → CONFIRMANDO", "CONFIRMANDO", m.estado)
    assert_verdadero(MOD, "  F10: respuesta contiene 'salsa'",
        "salsa" in resp.lower())

    subseccion("Resumen del pedido — formato correcto")
    m = nuevo_mesero()
    m.transicion("dame una vegana sin cebolla con queso")
    resp = m.transicion("si")
    assert_verdadero(MOD, "  resumen contiene nombre del producto",
        "vegana" in resp.lower())


# ══════════════════════════════════════════════════════════════
#  REPORTE FINAL
# ══════════════════════════════════════════════════════════════

def reporte_final():
    print(f"\n{BOLD}{'═'*55}{RESET}")
    print(f"{BOLD}  RESULTADO FINAL{RESET}")
    print(f"{BOLD}{'═'*55}{RESET}")

    total = total_ok + total_fail
    pct   = (total_ok / total * 100) if total > 0 else 0

    print(f"  Total pruebas : {total}")
    print(f"  {VERDE}Pasaron       : {total_ok}{RESET}")
    if total_fail > 0:
        print(f"  {ROJO}Fallaron      : {total_fail}{RESET}")
    else:
        print(f"  Fallaron      : 0")

    barra_ok   = "█" * int(pct / 2)
    barra_fail = "░" * (50 - int(pct / 2))
    color = VERDE if pct == 100 else (CYAN if pct >= 80 else ROJO)
    print(f"\n  {color}{barra_ok}{barra_fail}{RESET}  {pct:.1f}%\n")

    if fallos:
        print(f"  {BOLD}{ROJO}PRUEBAS FALLIDAS:{RESET}")
        for modulo, nombre, esp, obt in fallos:
            print(f"  {ROJO}✗{RESET} [{modulo}] {nombre}")
            print(f"      esperado : {esp}")
            print(f"      obtenido : {obt}")
        print()
    else:
        print(f"  {VERDE}{BOLD}🎉 ¡Todas las pruebas pasaron!{RESET}\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{BOLD}ParseBurger — Suite de Pruebas Completa{RESET}")
    print(f"{GRIS}Ejecutando todos los módulos...{RESET}")

    suite = [
        ("Tokenizador",     test_tokenizador),
        ("Parser CFG",      test_parser_cfg),
        ("DCG",             test_dcg),
        ("Ambigüedad+PCFG", test_ambiguedad_pcfg),
        ("ATN Mesero",      test_atn),
    ]

    for nombre, fn in suite:
        try:
            fn()
        except Exception as e:
            print(f"\n  {ROJO}ERROR INESPERADO en {nombre}:{RESET}")
            traceback.print_exc()
            fail(nombre, f"Error de ejecución en {nombre}", "sin excepción", str(e))

    reporte_final()