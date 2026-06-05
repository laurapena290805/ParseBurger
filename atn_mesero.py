# ============================================================
#  ParseBurger — Módulo 6: ATN — Mesero Virtual
#  Clase 8 — "ATN de diálogo"
#
#  Arquitectura siguiendo los ejemplos de la profesora (ATN.py):
#    - Tabla de transiciones como diccionario separado
#    - Subredes explícitas por estado (como red_np, red_vp, red_s)
#    - Motor de transición separado de la lógica de cada estado
#
#  Estados:
#    INICIO      → saludo + menú
#    ESCUCHANDO  → recibe y analiza el pedido
#    AMBIGUO     → espera resolución A o B
#    CONFIRMANDO → muestra resumen, espera confirmación
#    FIN         → pedido cerrado
# ============================================================

from gramatica   import grammar
from parser      import parse, parse_todos
from lexico      import dcg_parse_pedido, dcg_parse_lista_pedidos
from ambiguedad import detectar_ambiguedad, pcfg_score, mejor_arbol_pcfg
from tokenizador     import tokenizar

# ── Tabla de transiciones ─────────────────────────────────────
# El diagrama de estados en código — igual a dialogo_atn en ATN.py

DIALOGO_ATN = {
    "INICIO":      {"inicio":              "ESCUCHANDO"},
    "ESCUCHANDO":  {"pedido_valido":        "CONFIRMANDO",
                    "pedido_ambiguo":       "AMBIGUO",
                    "entrada_invalida":     "ESCUCHANDO",
                    "error_concordancia":   "ESCUCHANDO",
                    "no_reconocido":        "ESCUCHANDO"},
    "AMBIGUO":     {"resolucion_a":         "CONFIRMANDO",
                    "resolucion_b":         "CONFIRMANDO",
                    "invalido":             "AMBIGUO"},
    "CONFIRMANDO": {"confirmar":            "FIN",
                    "cancelar":             "ESCUCHANDO"},
    "FIN":         {}
}


class ATNMesero:
    """
    ATN del mesero virtual.

    Subredes (análogo a red_np, red_vp, red_s del archivo ATN.py):
      _subred_inicio()       → saluda y muestra el menú
      _subred_escuchando()   → analiza el pedido (CFG + DCG)
      _subred_ambiguo()      → resuelve la ambigüedad
      _subred_confirmando()  → confirma o cancela

    Cada subred devuelve (arco, respuesta).
    El motor consulta DIALOGO_ATN con ese arco para actualizar el estado.
    """

    MENU = """
╔══════════════════════════════════════════════╗
║         🍔  MENÚ PARSEBURGER  🍔            ║
╠══════════════════════════════════════════════╣
║  HAMBURGUESAS                                ║
║  · Clásica     ......................... $8  ║
║  · Doble       ........................$11   ║
║  · Especial    ........................$12   ║
║  · Vegana      ........................$10   ║
╠══════════════════════════════════════════════╣
║  MODIFICADORES   sin · con · extra           ║
║  INGREDIENTES    cebolla · queso · tomate    ║
║                  lechuga · pepinillo         ║
║                  mayonesa · mostaza · ketchup║
║                  carne · tocino · salsa      ║
╚══════════════════════════════════════════════╝"""

    def __init__(self):
        self.estado             = "INICIO"
        self.pedido_actual      = None
        self.patron_ambiguo     = None
        self.args_ambiguos      = []
        self._tokens_pendientes = []
        self.historial          = []

    # ── Motor de transición ───────────────────────────────────

    def transicion(self, entrada_usuario):
        """
        Función de transición de la ATN.
        Recibe texto → consulta la tabla → cambia estado → devuelve respuesta.

        Todas las subredes devuelven (arco, respuesta).
        El motor usa el arco para buscar el siguiente estado en DIALOGO_ATN.
        """
        entrada = entrada_usuario.strip().lower()
        self.historial.append(("usuario", entrada_usuario))

        if self.estado == "INICIO":
            arco, respuesta = self._subred_inicio()
        elif self.estado == "ESCUCHANDO":
            arco, respuesta = self._subred_escuchando(entrada)
        elif self.estado == "AMBIGUO":
            arco, respuesta = self._subred_ambiguo(entrada)
        elif self.estado == "CONFIRMANDO":
            arco, respuesta = self._subred_confirmando(entrada)
        elif self.estado == "FIN":
            arco, respuesta = None, "El pedido ya fue procesado. ¡Hasta pronto!"
        else:
            arco, respuesta = None, "Estado no reconocido."

        # ── Motor: consulta la tabla para actualizar el estado ──
        # el estado NO se cambia dentro de las subredes,
        # sino aquí, usando DIALOGO_ATN como fuente de verdad.
        if arco and arco in DIALOGO_ATN.get(self.estado, {}):
            self.estado = DIALOGO_ATN[self.estado][arco]

        self.historial.append(("mesero", respuesta))
        return respuesta

    # ── Subredes ──────────────────────────────────────────────
    # Cada subred devuelve (arco, respuesta).
    # El arco es la etiqueta del arco que se disparó (debe coincidir
    # con las claves de DIALOGO_ATN). El motor hace la transición.

    def _subred_inicio(self):
        """INICIO → devuelve arco 'inicio' para pasar a ESCUCHANDO."""
        respuesta = "¡Bienvenido a ParseBurger! 🍔\n" + self.MENU + "\n\n¿Qué desea ordenar?"
        return "inicio", respuesta

    def _subred_escuchando(self, entrada):
        """
        Subred principal — analiza la entrada con CFG + DCG.

        Arcos de salida:
          entrada_invalida    → error, queda en ESCUCHANDO
          pedido_ambiguo      → pide A/B, pasa a AMBIGUO
          error_concordancia  → avisa, queda en ESCUCHANDO
          pedido_valido       → pasa a CONFIRMANDO
          no_reconocido       → pide reformulación, queda en ESCUCHANDO
        """
        tokens = tokenizar(entrada)

        # Arco 1 — Entrada inválida (ítem fuera del menú)
        arbol_inv, pos_inv = parse("ENTRADA_INVALIDA", tokens, 0, grammar)
        if arbol_inv is not None and pos_inv == len(tokens):
            return "entrada_invalida", (
                "Lo siento, mi vocabulario solo me permite procesar pedidos "
                "de nuestro menú de hamburguesas.\n"
                "¿Qué te gustaría ordenar de nuestro catálogo?"
            )

        # Arco 2 — Ambigüedad léxica por patrón "sin X y Y"
        patron, args = detectar_ambiguedad(tokens)
        if patron is not None:
            self.patron_ambiguo     = patron
            self.args_ambiguos      = args
            self._tokens_pendientes = tokens
            return "pedido_ambiguo", patron["mensaje"].format(*args)

        # Arco 3 — CFG: todos los árboles posibles
        todos   = parse_todos("PEDIDO", tokens, 0, grammar)
        validos = [(n, p) for n, p in todos if p == len(tokens)]

        if len(validos) > 1:
            mejor = mejor_arbol_pcfg(validos)
            self.pedido_actual = dcg_parse_lista_pedidos(tokens) or [{}]
            respuesta = (
                f"Detecté {len(validos)} interpretaciones posibles.\n"
                f"Asumo la más probable (PCFG score={pcfg_score(mejor[0]):.4f}):\n"
                f"{self._resumen_pedido()}\n"
                "¿Es correcto? (sí / no)"
            )
            return "pedido_valido", respuesta

        if len(validos) == 0:
            return "no_reconocido", (
                "No pude interpretar tu pedido.\n"
                "Usa la forma: '[quiero/dame] [cantidad] [producto] [sin/con ingrediente]*'\n"
                "Ejemplo: 'quiero dos hamburguesas sin cebolla con queso'\n"
                "¿Deseas intentarlo de nuevo?"
            )

        # Arco 4 — DCG: verificar concordancia (soporta múltiples productos)
        resultado_dcg = dcg_parse_lista_pedidos(tokens)
        if resultado_dcg is None:
            return "error_concordancia", (
                "Hay un problema de concordancia en tu pedido.\n"
                "Ejemplo incorrecto: 'un hamburguesas' o 'una doble'.\n"
                "¿Podrías reformularlo?"
            )

        self.pedido_actual = resultado_dcg
        return "pedido_valido", (
            f"Pedido registrado:\n{self._resumen_pedido()}\n"
            "¿Desea confirmar su orden? (sí / no)"
        )

    def _subred_ambiguo(self, entrada):
        """
        AMBIGUO — espera que el usuario elija A o B.
        Arcos: resolucion_a / resolucion_b → CONFIRMANDO
               invalido (bucle) → AMBIGUO
        """
        if entrada in ("a", "b"):
            idx  = 0 if entrada == "a" else 1
            mods = self.patron_ambiguo["interpretaciones"][idx](*self.args_ambiguos)
            resultado_dcg = dcg_parse_lista_pedidos(self._tokens_pendientes) or [{}]
            resultado_dcg[0]["modificadores"] = mods
            self.pedido_actual = resultado_dcg
            arco = "resolucion_a" if entrada == "a" else "resolucion_b"
            respuesta = (
                f"Entendido, opción {entrada.upper()}.\n"
                f"Pedido registrado:\n{self._resumen_pedido()}\n"
                "¿Desea confirmar su orden? (sí / no)"
            )
            return arco, respuesta

        return "invalido", "Por favor responde A o B para resolver la ambigüedad."

    def _subred_confirmando(self, entrada):
        """
        CONFIRMANDO — espera sí o no.
        Arcos: confirmar → FIN  |  cancelar → ESCUCHANDO
        """
        if entrada in ("si", "sí", "s", "yes", "confirmar"):
            respuesta = (
                "✅ ¡Pedido confirmado!\n"
                f"{self._resumen_pedido()}\n"
                "Tu pedido está en preparación. ¡Que lo disfrutes! 🍔"
            )
            return "confirmar", respuesta

        if entrada in ("no", "cancelar", "n"):
            self.pedido_actual = None
            return "cancelar", "Pedido cancelado. ¿Deseas ordenar otra cosa?"

        return "invalido", "Por favor responde 'sí' para confirmar o 'no' para cancelar."

    # ── Helper: resumen del pedido ────────────────────────────

    def _resumen_pedido(self):
        if not self.pedido_actual:
            return "(sin pedido)"
        # pedido_actual es siempre una lista de dicts (uno por sub-pedido)
        pedidos = self.pedido_actual if isinstance(self.pedido_actual, list) else [self.pedido_actual]
        simbolo = {"NEG": "-", "POS": "+", "EXTRA": "x2"}
        lineas  = []
        for p in pedidos:
            cant     = p.get("cantidad_token", "?")
            prod     = p.get("producto", "?")
            mods     = p.get("modificadores", [])
            mods_str = ", ".join(
                f"{simbolo.get(m['tipo'], '?')}{m['ing']}" for m in mods
            ) if mods else "sin modificaciones"
            lineas.append(f"  {cant} {prod}. Modificaciones: {mods_str}.")
        return "\n".join(lineas)