# ============================================================
#  ParseBurger — Módulo 1: Gramática CFG
#  Clase 6 — "Representar la CFG como diccionario en Python"
#
#  Contiene SOLO las reglas estructurales.
#  Las palabras y sus rasgos viven en lexico_dcg.py (DCG).
# ============================================================

grammar = {
    "S": [
        ["PEDIDO"],
        ["ENTRADA_INVALIDA"]
    ],

    "PEDIDO": [
        ["VERBO_PEDIR", "NP_LIST"]
    ],

    # NP_LIST permite pedir varios productos en un mismo turno:
    # "quiero una clasica y una vegana"
    # "quiero dos hamburguesas una clasica y otra vegana"
    "NP_LIST": [
        ["NP_PEDIDO", "CONJ", "NP_LIST"],
        ["NP_PEDIDO"]
    ],

    "NP_PEDIDO": [
        ["CANTIDAD", "PRODUCTO"],
        ["CANTIDAD", "PRODUCTO", "MOD_LIST"]
    ],

    "VERBO_PEDIR": [
        ["quiero"], ["dame"], ["quisiera"], ["ponme"]
    ],

    "CANTIDAD": [
        ["un"], ["una"], ["dos"], ["tres"], ["cuatro"], ["cinco"]
    ],

    # PRODUCTO acepta tipo suelto o "hamburguesa + adjetivo"
    "PRODUCTO": [
        ["TIPO_BURGER"],
        ["hamburguesa", "ADJETIVO_BURGER"],
        ["hamburguesas", "ADJETIVO_BURGER"]
    ],
    "ADJETIVO_BURGER": [
        ["clasica"], ["clasicas"],
        ["doble"], ["dobles"],
        ["especial"], ["especiales"],
        ["vegana"], ["veganas"]
    ],

    "TIPO_BURGER": [
        ["hamburguesa"], ["hamburguesas"],
        ["clasica"], ["clasicas"],
        ["doble"], ["dobles"], 
        ["especial"], ["especiales"], 
        ["vegana"], ["veganas"]
    ],

    # MOD_LIST — sin recursión izquierda.
    # Genera AMBIGÜEDAD intencional con "sin X y Y":
    #   ¿(sin X) y (con Y)  vs  sin (X y Y)?
    "MOD_LIST": [
        ["MOD", "MOD_LIST_TAIL"],
        ["MOD"]
    ],
    "MOD_LIST_TAIL": [
        ["CONJ",  "MOD", "MOD_LIST_TAIL"],
        ["pero",  "MOD", "MOD_LIST_TAIL"],
        ["CONJ",  "MOD"],
        ["pero",  "MOD"],
        # Coordinación de ingredientes bajo el mismo operador:
        # "con queso y tocino" → CONJ INGREDIENTE hereda el tipo del MOD anterior
        ["CONJ",  "INGREDIENTE", "MOD_LIST_TAIL"],
        ["CONJ",  "INGREDIENTE"],
        ["MOD",   "MOD_LIST_TAIL"],   # cadena implícita: "sin X sin Y"
        ["MOD"]
    ],

    "MOD": [
        ["NEG",    "INGREDIENTE"],
        ["POS",    "INGREDIENTE"],
        ["EXTRA",  "INGREDIENTE"],
        ["POS",    "EXTRA",    "INGREDIENTE"],    # "con extra queso"
        ["POS",    "INTENSIF", "INGREDIENTE"]     # "con mucho queso"
    ],

    "NEG":     [["sin"]],
    "POS":     [["con"]],
    "EXTRA":   [["extra"], ["doble"]],
    "INTENSIF":[["mucho"], ["bastante"], ["poco"]],
    "CONJ":    [["y"]],

    "INGREDIENTE": [
        ["cebolla"], ["queso"], ["tomate"], ["lechuga"], ["salsa"],
        ["pepinillo"], ["mayonesa"], ["mostaza"],
        ["ketchup"], ["carne"], ["tocino"]
    ],

    # Entradas inválidas — Caso 3 del enunciado
    "ENTRADA_INVALIDA": [
        ["VERBO_PEDIR", "CANTIDAD",  "ITEM_INVALIDO"],
        ["VERBO_PEDIR",              "ITEM_INVALIDO"]
    ],

    "ITEM_INVALIDO": [
        ["perro_caliente"], ["pizza"], ["hotdog"], ["tacos"]
    ]
}