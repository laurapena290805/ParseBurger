import nltk

grammar = {
    "S": [
        ["PEDIDO"], ["ENTRADA_INVALIDA"]
    ],

    "PEDIDO": [
        ["VERBO_PEDIR", "NP_PEDIDO"]
    ],

    "NP_PEDIDO": [
        ["CANTIDAD", "PRODUCTO"], ["CANTIDAD", "PRODUCTO", "MOD_LIST"]
    ],

    "VERBO_PEDIR": [
        ["quiero"], ["dame"], ["quisiera"], ["ponme"]
    ],

    "CANTIDAD": [
        ["un"], ["una"], ["dos"], ["tres"], ["cuatro"], ["cinco"]
    ],

    "PRODUCTO": [
        ["TIPO_BURGER"]
    ],

    "TIPO_BURGER": [
        ["hamburguesa"], ["hamburguesas"], ["clasica"], ["doble"], ["especial"], ["vegana"]
    ],

    "MOD_LIST": [
        ["MOD"], ["MOD_LIST", "CONJ", "MOD"], ["MOD_LIST", "pero", "MOD"]
    ],

    "MOD": [
        ["NEG", "INGREDIENTE"], ["POS", "INGREDIENTE"],["EXTRA", "INGREDIENTE"]
    ],

    "NEG":   [["sin"]],
    "POS":   [["con"]],
    "EXTRA": [["extra"], ["doble"]],
    "CONJ":  [["y"]],

    "INGREDIENTE": [
        ["cebolla"], ["queso"], ["tomate"], ["lechuga"], ["pepinillo"], ["mayonesa"], ["mostaza"],
        ["ketchup"], ["carne"], ["tocino"]
    ],

    "ENTRADA_INVALIDA": [
        ["VERBO_PEDIR", "CANTIDAD", "ITEM_INVALIDO"], ["VERBO_PEDIR", "ITEM_INVALIDO"]
    ],

    "ITEM_INVALIDO": [
        ["perro_caliente"], ["pizza"], ["hotdog"], ["tacos"]
    ]
}