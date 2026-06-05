# ============================================================
#  ParseBurger — Módulo 4: Ambigüedad + PCFG
#  Clase 6 — "Detectando ambigüedad"
#
#  detectar_ambiguedad() — busca patrones léxicos ambiguos
#                          ANTES de parsear.
#  pcfg_score()          — calcula la probabilidad de un árbol.
#  mejor_arbol_pcfg()    — elige el árbol más probable cuando
#                          hay ambigüedad estructural.
# ============================================================

from parser import Nodo
from lexico  import lexico_dcg

# ── Patrones de ambigüedad ────────────────────────────────────
# "sin tomate y lechuga" → dos lecturas posibles:
#   (A) sin tomate  Y  sin lechuga  — excluir ambos
#   (B) sin tomate, pero con lechuga — solo excluir tomate

PATRONES_AMBIGUOS = [
    {
        "patron": ["sin", "<ING>", "y", "<ING>"],
        "mensaje": (
            "He detectado una ambigüedad sintáctica.\n"
            "¿Te refieres a:\n"
            "  (A) 'sin {0} y sin {1}' — excluir ambos ingredientes, o\n"
            "  (B) 'sin {0}, pero con {1}' — solo excluir {0}?\n"
            "Responde A o B para continuar."
        ),
        "interpretaciones": [
            lambda a, b: [{"tipo": "NEG", "ing": a}, {"tipo": "NEG", "ing": b}],
            lambda a, b: [{"tipo": "NEG", "ing": a}, {"tipo": "POS", "ing": b}],
        ]
    }
]


def detectar_ambiguedad(tokens):
    """
    Busca patrones ambiguos en la secuencia de tokens.
    Retorna (patron_def, args) o (None, None).
    """
    for patron_def in PATRONES_AMBIGUOS:
        patron = patron_def["patron"]
        for i in range(len(tokens) - len(patron) + 1):
            ventana = tokens[i:i + len(patron)]
            match   = True
            args    = []
            for p, t in zip(patron, ventana):
                if p == "<ING>":
                    if lexico_dcg.get(t, {}).get("cat") == "INGREDIENTE":
                        args.append(t)
                    else:
                        match = False
                        break
                elif p != t:
                    match = False
                    break
            if match:
                return patron_def, args
    return None, None


# ── PCFG — probabilidades por producción ─────────────────────

PCFG_PROBS = {
    "MOD_LIST": {
        ("MOD", "MOD_LIST_TAIL"): 0.60,   # "sin cebolla con queso"
        ("MOD",):                 0.40,   # "sin cebolla"
    },
    "MOD_LIST_TAIL": {
        ("CONJ",  "MOD", "MOD_LIST_TAIL"): 0.25,
        ("pero",  "MOD", "MOD_LIST_TAIL"): 0.10,
        ("CONJ",  "MOD"):                  0.20,
        ("pero",  "MOD"):                  0.10,
        ("CONJ",  "INGREDIENTE", "MOD_LIST_TAIL"): 0.10,
        ("CONJ",  "INGREDIENTE"):           0.10,
        ("MOD",   "MOD_LIST_TAIL"):         0.10,
        ("MOD",):                           0.05,
    },
    "MOD": {
        ("NEG",   "INGREDIENTE"):            0.45,
        ("POS",   "INGREDIENTE"):            0.35,
        ("EXTRA", "INGREDIENTE"):            0.05,
        ("POS",   "EXTRA",    "INGREDIENTE"): 0.10,
        ("POS",   "INTENSIF", "INGREDIENTE"): 0.05,
    }
}
 


def pcfg_score(arbol):
    """Calcula la probabilidad de un árbol según la PCFG."""
    score = 1.0

    def recorrer(nodo):
        nonlocal score
        if not isinstance(nodo, Nodo):
            return
        if nodo.etiqueta in PCFG_PROBS:
            prod_usada = tuple(
                h.etiqueta if isinstance(h, Nodo) else h
                for h in nodo.hijos
            )
            score *= PCFG_PROBS[nodo.etiqueta].get(prod_usada, 0.01)
        for hijo in nodo.hijos:
            recorrer(hijo)

    recorrer(arbol)
    return score


def mejor_arbol_pcfg(arboles_validos):
    """Retorna el árbol con mayor probabilidad PCFG."""
    if not arboles_validos:
        return None
    return max(arboles_validos, key=lambda par: pcfg_score(par[0]))