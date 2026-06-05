# ============================================================
#  test_parseburger_detallado.py
#  Suite de pruebas con mensajes de error específicos
#  Ejecutar: python test_parseburger_detallado.py
# ============================================================

import sys
import traceback
from typing import Any, Tuple, Optional, List, Dict

# ── Colores para la terminal ──────────────────────────────────
VERDE  = "\033[92m"
ROJO   = "\033[91m"
AMARILLO = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
GRIS   = "\033[90m"

# ── Contadores globales ───────────────────────────────────────
total_ok = 0
total_fail = 0
fallos_detallados = []  # (módulo, nombre, esperado, obtenido, explicacion)

def formatear_valor(valor, max_len=50):
    """Formatea un valor para mostrarlo en el reporte."""
    if valor is None:
        return "None"
    if isinstance(valor, str) and len(valor) > max_len:
        return valor[:max_len] + "..."
    if isinstance(valor, list):
        if len(valor) > 10:
            return f"[{len(valor)} elementos]"
        return str(valor)
    if isinstance(valor, dict):
        if len(valor) > 5:
            claves = list(valor.keys())[:5]
            return f"{{{', '.join(claves)}...}} ({len(valor)} claves)"
        return str(valor)
    return str(valor)

def ok(modulo, nombre):
    global total_ok
    total_ok += 1
    print(f"  {VERDE}✓{RESET} {nombre}")

def fail(modulo, nombre, esperado, obtenido, explicacion=None):
    global total_fail
    total_fail += 1
    fallos_detallados.append((modulo, nombre, esperado, obtenido, explicacion))
    print(f"  {ROJO}✗{RESET} {nombre}")
    print(f"    {GRIS}esperado : {formatear_valor(esperado)}{RESET}")
    print(f"    {GRIS}obtenido : {formatear_valor(obtenido)}{RESET}")
    if explicacion:
        print(f"    {AMARILLO}razón    : {explicacion}{RESET}")

def seccion(titulo):
    print(f"\n{BOLD}{CYAN}{'═'*60}{RESET}")
    print(f"{BOLD}{CYAN}  {titulo}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*60}{RESET}")

def subseccion(titulo):
    print(f"\n  {BOLD}── {titulo} ──{RESET}")

def assert_igual(modulo, nombre, esperado, obtenido, explicacion=None):
    if esperado == obtenido:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, esperado, obtenido, explicacion)

def assert_verdadero(modulo, nombre, condicion, detalle=""):
    if condicion:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, "True", f"False {detalle}", detalle if detalle else "Condición falsa")

def assert_nulo(modulo, nombre, valor, explicacion=None):
    if valor is None:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, "None", valor, explicacion)

def assert_no_nulo(modulo, nombre, valor, explicacion=None):
    if valor is not None:
        ok(modulo, nombre)
    else:
        fail(modulo, nombre, "valor no None", None, explicacion)


# ══════════════════════════════════════════════════════════════
#  1. TOKENIZADOR
# ══════════════════════════════════════════════════════════════

def test_tokenizador():
    seccion("1. TOKENIZADOR")
    from tokenizador import tokenizar
    MOD = "Tokenizador"

    subseccion("Normalización básica")
    
    # Prueba 1: minúsculas
    entrada = "QUIERO UNA CLASICA"
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "minúsculas", esperado, obtenido,
        f"El tokenizador debe convertir todo a minúsculas. Entrada: '{entrada}'")

    # Prueba 2: eliminación de puntuación
    entrada = "quiero, una clásica."
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "elimina puntuación", esperado, obtenido,
        f"El tokenizador debe eliminar comas y puntos. Entrada: '{entrada}'")

    # Prueba 3: eliminación de tildes
    entrada = "quiero una clásica"
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "elimina tildes (á→a, é→e, í→i, ó→o, ú→u)", esperado, obtenido,
        f"El tokenizador debe reemplazar tildes. 'clásica' → 'clasica'")

    # Prueba 4: tildes en mayúsculas
    entrada = "DÁME UNA CLÁSICA"
    esperado = ["dame", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "tildes en mayúsculas", esperado, obtenido,
        f"El tokenizador debe manejar tildes en mayúsculas")

    subseccion("Palabras ignoradas")
    
    # Prueba 5: ignorar 'por'
    entrada = "por quiero una clasica"
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "ignora 'por'", esperado, obtenido,
        f"La palabra 'por' debe ser eliminada del token list")

    # Prueba 6: ignorar 'favor'
    entrada = "quiero una clasica favor"
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "ignora 'favor'", esperado, obtenido,
        f"La palabra 'favor' debe ser eliminada")

    # Prueba 7: ignorar 'me'
    entrada = "me dame una clasica"
    esperado = ["dame", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "ignora 'me'", esperado, obtenido,
        f"La palabra 'me' debe ser eliminada")

    # Prueba 8: ignorar 'pedir'
    entrada = "pedir quiero una clasica"
    esperado = ["quiero", "una", "clasica"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "ignora 'pedir'", esperado, obtenido,
        f"La palabra 'pedir' debe ser eliminada")

    subseccion("Frases multi-palabra")
    
    # Prueba 9: perro caliente → perro_caliente
    entrada = "quiero un perro caliente"
    esperado = ["quiero", "un", "perro_caliente"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "perro caliente → perro_caliente", esperado, obtenido,
        f"La frase 'perro caliente' debe convertirse en un solo token 'perro_caliente'")

    # Prueba 10: hot dog → hotdog
    entrada = "quiero un hot dog"
    esperado = ["quiero", "un", "hotdog"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "hot dog → hotdog", esperado, obtenido,
        f"La frase 'hot dog' debe convertirse en 'hotdog'")

    # Prueba 11: múltiples frases
    entrada = "dame un perro-caliente y una hamburguesa"
    esperado = ["dame", "un", "perro_caliente", "y", "una", "hamburguesa"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "perro-caliente con guión", esperado, obtenido,
        f"Formato con guión 'perro-caliente' debe normalizarse a 'perro_caliente'")

    subseccion("Casos completos")
    
    # Prueba 12: pedido completo
    entrada = "quiero dos hamburguesas sin cebolla con queso"
    esperado = ["quiero", "dos", "hamburguesas", "sin", "cebolla", "con", "queso"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "pedido completo con modificadores", esperado, obtenido,
        f"El tokenizador debe preservar el orden y los modificadores")

    # Prueba 13: palabra 'y' debe preservarse
    entrada = "quiero una clasica sin tomate y lechuga"
    esperado = ["quiero", "una", "clasica", "sin", "tomate", "y", "lechuga"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "preserva 'y' (conjunción)", esperado, obtenido,
        f"La palabra 'y' es importante para detectar ambigüedad, no debe eliminarse")

    # Prueba 14: palabra 'pero' debe preservarse
    entrada = "quiero una clasica sin cebolla pero con queso"
    esperado = ["quiero", "una", "clasica", "sin", "cebolla", "pero", "con", "queso"]
    obtenido = tokenizar(entrada)
    assert_igual(MOD, "preserva 'pero' (conjunción adversativa)", esperado, obtenido,
        f"La palabra 'pero' es importante para la estructura del pedido")


# ══════════════════════════════════════════════════════════════
#  2. PARSER CFG
# ══════════════════════════════════════════════════════════════

def test_parser_cfg():
    seccion("2. PARSER CFG")
    from tokenizador import tokenizar
    from gramatica import grammar
    from parser import parse, parse_todos
    MOD = "Parser CFG"

    def acepta_s(entrada):
        tokens = tokenizar(entrada)
        todos = parse_todos("S", tokens, 0, grammar)
        return [(n, p) for n, p in todos if p == len(tokens)]

    def acepta_pedido(entrada):
        tokens = tokenizar(entrada)
        todos = parse_todos("PEDIDO", tokens, 0, grammar)
        return [(n, p) for n, p in todos if p == len(tokens)]

    subseccion("Pedidos válidos — deben aceptarse")
    
    # Prueba 1: un doble
    entrada = "dame un doble"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "un doble", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada por la gramática. Se encontraron {len(resultado)} árboles.")

    # Prueba 2: una clasica
    entrada = "quiero una clasica"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "una clasica", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada")

    # Prueba 3: dos hamburguesas
    entrada = "quiero dos hamburguesas"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "dos hamburguesas", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada")

    # Prueba 4: con extra
    entrada = "ponme una especial con extra tocino"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "pedido con extra: con extra tocino", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada (soporta 'extra')")

    # Prueba 5: con salsa (Error 1 del enunciado)
    entrada = "quiero una clasica con salsa"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "pedido con salsa (FIX Error 1)", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada. 'salsa' debe estar en INGREDIENTE")

    # Prueba 6: hamburguesa + adjetivo
    entrada = "quiero una hamburguesa clasica"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "hamburguesa + adjetivo: hamburguesa clasica", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada (producto compuesto)")

    # Prueba 7: lista de pedidos
    entrada = "quiero una clasica y una vegana"
    resultado = acepta_pedido(entrada)
    assert_verdadero(MOD, "lista de pedidos: una clasica y una vegana", len(resultado) >= 1,
        f"La entrada '{entrada}' debería ser aceptada (NP_LIST)")

    subseccion("Entradas inválidas — deben rechazarse como PEDIDO")
    
    # Prueba 8: perro_caliente no es PEDIDO
    entrada = "quiero un perro_caliente"
    resultado = acepta_pedido(entrada)
    assert_igual(MOD, "perro_caliente → no es PEDIDO válido", 0, len(resultado),
        f"'{entrada}' no es un pedido válido (ítem fuera del menú)")

    # Prueba 9: pizza no es PEDIDO
    entrada = "quiero una pizza"
    resultado = acepta_pedido(entrada)
    assert_igual(MOD, "pizza → no es PEDIDO válido", 0, len(resultado),
        f"'{entrada}' no es un pedido válido (pizza no está en el menú)")

    subseccion("Entradas inválidas — detectadas por ENTRADA_INVALIDA")
    
    def es_invalida(entrada):
        tokens = tokenizar(entrada)
        arbol, pos = parse("ENTRADA_INVALIDA", tokens, 0, grammar)
        return arbol is not None and pos == len(tokens)

    # Prueba 10: perro_caliente debe ser ENTRADA_INVALIDA
    entrada = "quiero un perro_caliente"
    assert_verdadero(MOD, "perro_caliente → ENTRADA_INVALIDA", es_invalida(entrada),
        f"'{entrada}' debería reconocerse como ENTRADA_INVALIDA")

    # Prueba 11: pizza debe ser ENTRADA_INVALIDA
    entrada = "dame una pizza"
    assert_verdadero(MOD, "pizza → ENTRADA_INVALIDA", es_invalida(entrada),
        f"'{entrada}' debería reconocerse como ENTRADA_INVALIDA")


# ══════════════════════════════════════════════════════════════
#  3. DCG — UNIFICACIÓN Y CONCORDANCIA
# ══════════════════════════════════════════════════════════════

def test_dcg():
    seccion("3. DCG — UNIFICACIÓN Y CONCORDANCIA")
    from lexico import unificar, dcg_parse_pedido, dcg_parse_lista_pedidos, CONCORDANCIA_GEN
    from tokenizador import tokenizar
    MOD = "DCG"

    subseccion("unificar() — casos base")
    
    # Prueba 1: unificación igual
    resultado = unificar({"num": "sg"}, {"num": "sg"})
    assert_igual(MOD, "unificar iguales: {num:sg} + {num:sg}", {"num": "sg"}, resultado,
        f"Unificar dos DAGs idénticos debe retornar el DAG combinado")

    # Prueba 2: conflicto numérico
    resultado = unificar({"num": "sg"}, {"num": "pl"})
    assert_nulo(MOD, "conflicto: {num:sg} + {num:pl} → None", resultado,
        f"Unificar sg con pl debe fallar (None)")

    # Prueba 3: merge sin conflicto
    resultado = unificar({"a": 1}, {"b": 2})
    assert_igual(MOD, "merge sin conflicto: {a:1} + {b:2}", {"a": 1, "b": 2}, resultado,
        f"Al unificar DAGs con claves diferentes, deben combinarse")

    # Prueba 4: conflicto de categoría
    resultado = unificar({"cat": "N"}, {"cat": "V"})
    assert_nulo(MOD, "conflicto en clave compartida → None", resultado,
        f"Unificar categorías diferentes (N vs V) debe fallar")

    subseccion("dcg_parse_pedido() — concordancia correcta")
    
    def dcg_ok(entrada):
        return dcg_parse_pedido(tokenizar(entrada))

    # Prueba 5: dos hamburguesas
    resultado = dcg_ok("quiero dos hamburguesas")
    assert_no_nulo(MOD, "dos hamburguesas → OK", resultado,
        f"'dos hamburguesas' debería pasar concordancia (gen neu+neu, num pl+pl)")

    if resultado:
        assert_igual(MOD, "  producto detectado: 'hamburguesas'", "hamburguesas", resultado["producto"])
        assert_igual(MOD, "  sin modificadores", [], resultado["modificadores"])

    # Prueba 6: una clasica
    resultado = dcg_ok("dame una clasica")
    assert_no_nulo(MOD, "una clasica → OK", resultado,
        f"'una clasica' debería pasar concordancia (fem+fem)")

    # Prueba 7: con modificadores
    entrada = "quiero una clasica con queso sin cebolla"
    resultado = dcg_ok(entrada)
    assert_no_nulo(MOD, "una clasica con queso sin cebolla → OK", resultado,
        f"'{entrada}' debería parsearse correctamente")
    
    if resultado:
        mods = resultado["modificadores"]
        if len(mods) != 2:
            fail(MOD, "  2 modificadores", 2, len(mods), f"Se esperaban 2 modificadores, se encontraron {len(mods)}")
        else:
            ok(MOD, "  2 modificadores")
            if mods[0].get("tipo") != "POS" or mods[0].get("ing") != "queso":
                fail(MOD, "  1er mod: +queso", {"tipo": "POS", "ing": "queso"}, mods[0],
                    f"El primer modificador debería ser 'con queso'")
            else:
                ok(MOD, "  1er mod: +queso")
            if mods[1].get("tipo") != "NEG" or mods[1].get("ing") != "cebolla":
                fail(MOD, "  2do mod: -cebolla", {"tipo": "NEG", "ing": "cebolla"}, mods[1],
                    f"El segundo modificador debería ser 'sin cebolla'")
            else:
                ok(MOD, "  2do mod: -cebolla")

    # Prueba 8: con extra
    resultado = dcg_ok("ponme una especial con extra tocino")
    assert_no_nulo(MOD, "una especial con extra tocino → OK", resultado,
        f"Debería reconocer 'con extra tocino' como modificador EXTRA")

    # Prueba 9: con salsa
    resultado = dcg_ok("quiero una clasica con salsa")
    assert_no_nulo(MOD, "con salsa → OK (FIX Error 1)", resultado,
        f"'salsa' debe estar en el léxico como INGREDIENTE")

    subseccion("dcg_parse_pedido() — errores de concordancia")
    
    # Prueba 10: un hamburguesas (sg + pl)
    resultado = dcg_ok("quiero un hamburguesas")
    assert_nulo(MOD, "FALLA: 'un hamburguesas' (sg + pl)", resultado,
        f"'un' es singular, 'hamburguesas' es plural → debe fallar concordancia de número")

    # Prueba 11: una doble (fem + masc)
    # Prueba 11: esto debería funcionar
    resultado = dcg_ok("dame una doble")
    assert_no_nulo(MOD, "OK: 'una doble' (fem + neu aceptado)", resultado)

    # Prueba 12: un vegana
    resultado = dcg_ok("quiero un vegana")
    assert_nulo(MOD, "FALLA: 'un vegana' (masc + fem)", resultado,
        f"'un' es masculino, 'vegana' es femenino → debe fallar")


# ══════════════════════════════════════════════════════════════
#  4. AMBIGÜEDAD + PCFG
# ══════════════════════════════════════════════════════════════

def test_ambiguedad_pcfg():
    seccion("4. AMBIGÜEDAD + PCFG")
    from tokenizador import tokenizar
    from ambiguedad import detectar_ambiguedad, pcfg_score, mejor_arbol_pcfg
    from gramatica import grammar
    from parser import parse_todos
    MOD = "Ambigüedad+PCFG"

    subseccion("detectar_ambiguedad() — patrones ambiguos")
    
    def ambiguo(entrada):
        return detectar_ambiguedad(tokenizar(entrada))

    # Prueba 1: sin tomate y lechuga
    entrada = "dame una clasica sin tomate y lechuga"
    patron, args = ambiguo(entrada)
    assert_no_nulo(MOD, "detecta 'sin X y Y' como ambiguo", patron,
        f"La entrada '{entrada}' contiene el patrón ambiguo 'sin X y Y'")
    
    if patron:
        assert_igual(MOD, "  args correctos: [tomate, lechuga]", ["tomate", "lechuga"], args,
            f"Los argumentos extraídos deberían ser 'tomate' y 'lechuga'")

    # Prueba 2: sin queso y cebolla
    entrada = "quiero una vegana sin queso y cebolla"
    patron, args = ambiguo(entrada)
    assert_no_nulo(MOD, "detecta 'sin queso y cebolla'", patron,
        f"La entrada '{entrada}' contiene el patrón ambiguo")
    
    if patron:
        assert_igual(MOD, "  args: [queso, cebolla]", ["queso", "cebolla"], args)

    subseccion("detectar_ambiguedad() — casos NO ambiguos")
    
    # Prueba 3: sin cebolla con queso
    entrada = "quiero una clasica sin cebolla con queso"
    patron, args = ambiguo(entrada)
    assert_nulo(MOD, "sin cebolla CON queso → no ambiguo", patron,
        f"El patrón 'sin X con Y' no es ambiguo")

    # Prueba 4: sin modificadores
    entrada = "dame dos hamburguesas"
    patron, args = ambiguo(entrada)
    assert_nulo(MOD, "sin modificadores → no ambiguo", patron)

    # Prueba 5: un solo ingrediente
    entrada = "quiero una clasica sin tomate"
    patron, args = ambiguo(entrada)
    assert_nulo(MOD, "un solo ingrediente negado → no ambiguo", patron,
        f"Se necesita 'y' para formar el patrón ambiguo")

    subseccion("Interpretaciones del patrón ambiguo")
    
    entrada = "dame una clasica sin tomate y lechuga"
    patron, args = ambiguo(entrada)
    if patron:
        interp_a = patron["interpretaciones"][0](*args)
        interp_b = patron["interpretaciones"][1](*args)
        
        esperado_a = [{"tipo": "NEG", "ing": "tomate"}, {"tipo": "NEG", "ing": "lechuga"}]
        esperado_b = [{"tipo": "NEG", "ing": "tomate"}, {"tipo": "POS", "ing": "lechuga"}]
        
        assert_igual(MOD, "Interp A: ambos negativos", esperado_a, interp_a,
            f"Interpretación A: sin tomate Y sin lechuga")
        
        assert_igual(MOD, "Interp B: primero neg, segundo pos", esperado_b, interp_b,
            f"Interpretación B: sin tomate, pero con lechuga")

    subseccion("pcfg_score() — valores razonables")
    
    entrada = "quiero dos hamburguesas sin cebolla con queso"
    tokens = tokenizar(entrada)
    todos = parse_todos("PEDIDO", tokens, 0, grammar)
    validos = [(n, p) for n, p in todos if p == len(tokens)]
    
    if len(validos) == 0:
        fail(MOD, "hay al menos 1 árbol para el pedido", "≥1", 0,
            f"No se pudo parsear la entrada '{entrada}'")
    else:
        ok(MOD, "hay al menos 1 árbol para el pedido")
        score = pcfg_score(validos[0][0])
        if score <= 0:
            fail(MOD, f"score > 0", ">0", score,
                f"El score PCFG debe ser positivo, pero es {score}")
        else:
            ok(MOD, f"score > 0 (obtenido: {score:.6f})")
        
        if score > 1.0:
            fail(MOD, f"score <= 1", "≤1", score,
                f"El score PCFG es una probabilidad, no puede superar 1.0")
        else:
            ok(MOD, f"score <= 1 (obtenido: {score:.6f})")


# ══════════════════════════════════════════════════════════════
#  5. ATN MESERO — FLUJOS COMPLETOS
# ══════════════════════════════════════════════════════════════

def test_atn():
    seccion("5. ATN MESERO — FLUJOS DE DIÁLOGO")
    from atn_mesero import ATNMesero
    MOD = "ATN"

    def nuevo_mesero():
        m = ATNMesero()
        m.transicion("inicio")
        return m

    subseccion("Estado inicial y transición de bienvenida")
    
    m = ATNMesero()
    if m.estado != "INICIO":
        fail(MOD, "estado inicial es INICIO", "INICIO", m.estado,
            f"El ATN debería comenzar en estado INICIO")
    else:
        ok(MOD, "estado inicial es INICIO")
    
    resp = m.transicion("inicio")
    if m.estado != "ESCUCHANDO":
        fail(MOD, "transición a ESCUCHANDO", "ESCUCHANDO", m.estado,
            f"Después de 'inicio', el estado debería ser ESCUCHANDO")
    else:
        ok(MOD, "transición a ESCUCHANDO")
    
    if "ParseBurger" not in resp:
        fail(MOD, "bienvenida contiene menú", "ParseBurger en respuesta", resp[:50],
            f"La respuesta de bienvenida debería contener el nombre del sistema")
    else:
        ok(MOD, "bienvenida contiene menú")

    subseccion("Flujo 1 — pedido válido → confirmar → FIN")
    
    m = nuevo_mesero()
    resp = m.transicion("quiero dos hamburguesas sin cebolla")
    
    if m.estado != "CONFIRMANDO":
        fail(MOD, "  F1: pasa a CONFIRMANDO", "CONFIRMANDO", m.estado,
            f"Después de un pedido válido, debería pasar a CONFIRMANDO")
    else:
        ok(MOD, "  F1: pasa a CONFIRMANDO")
    
    if "hamburguesas" not in resp.lower():
        fail(MOD, "  F1: respuesta contiene 'hamburguesas'", "'hamburguesas' en respuesta", resp[:50],
            f"La respuesta debería mostrar el pedido")
    else:
        ok(MOD, "  F1: respuesta contiene 'hamburguesas'")
    
    resp = m.transicion("si")
    if m.estado != "FIN":
        fail(MOD, "  F1: confirmar → FIN", "FIN", m.estado,
            f"Al confirmar (si), debería pasar a FIN")
    else:
        ok(MOD, "  F1: confirmar → FIN")
    
    if "confirmado" not in resp.lower() and "✅" not in resp:
        fail(MOD, "  F1: respuesta contiene confirmación", "'confirmado' o ✓", resp[:50],
            f"La respuesta debería confirmar el pedido")
    else:
        ok(MOD, "  F1: respuesta contiene confirmación")

    subseccion("Flujo 2 — pedido válido → cancelar → vuelve a ESCUCHANDO")
    
    m = nuevo_mesero()
    m.transicion("dame una clasica con queso")
    
    if m.estado != "CONFIRMANDO":
        fail(MOD, "  F2: en CONFIRMANDO", "CONFIRMANDO", m.estado,
            f"El pedido es válido, debería estar en CONFIRMANDO")
    else:
        ok(MOD, "  F2: en CONFIRMANDO")
    
    resp = m.transicion("no")
    if m.estado != "ESCUCHANDO":
        fail(MOD, "  F2: cancelar → ESCUCHANDO", "ESCUCHANDO", m.estado,
            f"Al cancelar (no), debería volver a ESCUCHANDO")
    else:
        ok(MOD, "  F2: cancelar → ESCUCHANDO")
    
    if "cancelad" not in resp.lower():
        fail(MOD, "  F2: respuesta menciona cancelación", "'cancelado' en respuesta", resp[:50],
            f"La respuesta debería indicar que se canceló el pedido")
    else:
        ok(MOD, "  F2: respuesta menciona cancelación")

    subseccion("Flujo 3 — ambigüedad, elige A")
    
    m = nuevo_mesero()
    resp = m.transicion("dame una clasica sin tomate y lechuga")
    
    if m.estado != "AMBIGUO":
        fail(MOD, "  F3: pasa a AMBIGUO", "AMBIGUO", m.estado,
            f"El patrón 'sin X y Y' es ambiguo, debería pasar a AMBIGUO")
    else:
        ok(MOD, "  F3: pasa a AMBIGUO")
    
    if "(A)" not in resp or "(B)" not in resp:
        fail(MOD, "  F3: pregunta A o B", "contiene (A) y (B)", resp[:80],
            f"La respuesta debería pedir elegir entre A y B")
    else:
        ok(MOD, "  F3: pregunta A o B")
    
    m.transicion("a")
    if m.estado != "CONFIRMANDO":
        fail(MOD, "  F3: resolución A → CONFIRMANDO", "CONFIRMANDO", m.estado,
            f"Al elegir A, debería pasar a CONFIRMANDO")
    else:
        ok(MOD, "  F3: resolución A → CONFIRMANDO")
    
    m.transicion("si")
    if m.estado != "FIN":
        fail(MOD, "  F3: confirmar → FIN", "FIN", m.estado,
            f"Después de confirmar, debería terminar en FIN")
    else:
        ok(MOD, "  F3: confirmar → FIN")


# ══════════════════════════════════════════════════════════════
#  REPORTE FINAL
# ══════════════════════════════════════════════════════════════

def reporte_final():
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}  RESULTADO FINAL{RESET}")
    print(f"{BOLD}{'═'*60}{RESET}")

    total = total_ok + total_fail
    pct = (total_ok / total * 100) if total > 0 else 0

    print(f"\n  Total pruebas : {total}")
    print(f"  {VERDE}Pasaron       : {total_ok}{RESET}")
    print(f"  {ROJO}Fallaron      : {total_fail}{RESET}")

    barra_ok = "█" * int(pct / 2)
    barra_fail = "░" * (50 - int(pct / 2))
    color = VERDE if pct == 100 else (AMARILLO if pct >= 80 else ROJO)
    print(f"\n  {color}{barra_ok}{barra_fail}{RESET}  {pct:.1f}%")

    if fallos_detallados:
        print(f"\n  {BOLD}{ROJO}━━━ PRUEBAS FALLIDAS ━━━{RESET}")
        for modulo, nombre, esperado, obtenido, explicacion in fallos_detallados:
            print(f"\n  {ROJO}✗{RESET} [{modulo}] {nombre}")
            print(f"      {GRIS}esperado :{RESET} {formatear_valor(esperado)}")
            print(f"      {GRIS}obtenido :{RESET} {formatear_valor(obtenido)}")
            if explicacion:
                print(f"      {AMARILLO}→ {explicacion}{RESET}")
    else:
        print(f"\n  {VERDE}{BOLD}🎉 ¡Todas las pruebas pasaron!{RESET}")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{BOLD}ParseBurger — Suite de Pruebas con Reporte Detallado{RESET}")
    print(f"{GRIS}Ejecutando todos los módulos...{RESET}")

    suite = [
        ("Tokenizador", test_tokenizador),
        ("Parser CFG", test_parser_cfg),
        ("DCG", test_dcg),
        ("Ambigüedad+PCFG", test_ambiguedad_pcfg),
        ("ATN Mesero", test_atn),
    ]

    for nombre, fn in suite:
        try:
            fn()
        except Exception as e:
            print(f"\n  {ROJO}ERROR INESPERADO en {nombre}:{RESET}")
            traceback.print_exc()
            fail(nombre, f"Error de ejecución en {nombre}", "sin excepción", str(e),
                f"Excepción lanzada: {type(e).__name__}: {e}")

    reporte_final()