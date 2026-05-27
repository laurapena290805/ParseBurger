# ============================================================
#  ParseBurger — main.py
#  Punto de entrada del proyecto
#
#  Ejecutar:  python main.py
#
#  Opciones:
#    1) Demo — los 3 casos del enunciado + casos extra
#    2) Conversación interactiva con el mesero (ATN)
#    3) Ambos
# ============================================================

from gramatica   import grammar
from parser      import parse, parse_todos
from lexico      import dcg_parse_pedido
from ambiguedad import detectar_ambiguedad, pcfg_score, mejor_arbol_pcfg
from tokenizador     import tokenizar
from atn_mesero      import ATNMesero


# ── Demo de casos de prueba ───────────────────────────────────

def demo_casos():
    print("=" * 60)
    print("  ParseBurger — Demo de casos de prueba")
    print("  (CFG + DCG + Ambigüedad + PCFG)")
    print("=" * 60)

    casos = [
        # Casos del enunciado
        ("Caso 1 — Pedido válido con modificadores",
         "quiero dos hamburguesas sin cebolla pero con extra queso"),

        ("Caso 2 — Ambigüedad sintáctica: 'sin X y Y'",
         "dame una clasica sin tomate y lechuga"),

        ("Caso 3 — Entrada inválida (ítem fuera del menú)",
         "quiero un perro_caliente"),

        # Casos adicionales
        ("Caso 4 — Pedido válido simple",
         "quisiera tres hamburguesas con queso"),

        ("Caso 5 — Pedido con extra",
         "ponme una especial con extra tocino sin mayonesa"),

        ("Caso 6 — Fallo de concordancia DCG (sg + pl)",
         "quiero un hamburguesas"),

        ("Caso 7 — Fallo de concordancia DCG (gen fem → gen masc)",
         "dame una doble"),

        ("Caso 8 — Árbol de derivación visible",
         "dame dos hamburguesas con queso sin cebolla"),
    ]

    for desc, entrada in casos:
        print(f"\n{'─'*60}")
        print(f"[{desc}]")
        print(f"Entrada : \"{entrada}\"")
        tokens = tokenizar(entrada)
        print(f"Tokens  : {tokens}")

        # CFG
        todos   = parse_todos("S", tokens, 0, grammar)
        validos = [(n, p) for n, p in todos if p == len(tokens)]
        print(f"Árboles válidos (CFG): {len(validos)}")

        if len(validos) > 1:
            mejor = mejor_arbol_pcfg(validos)
            print(f"Mejor árbol PCFG (score={pcfg_score(mejor[0]):.4f}):")
            print(mejor[0].mostrar())
        elif len(validos) == 1:
            print("Árbol de derivación:")
            print(validos[0][0].mostrar())

        # DCG
        dcg = dcg_parse_pedido(tokens)
        if dcg:
            num_c = dcg.get("cantidad_rasgos", {}).get("num", "?")
            num_p = dcg.get("producto_rasgos", {}).get("num", "?")
            print(f"DCG — concordancia OK. cant.num={num_c}, prod.num={num_p}")
        else:
            arbol_inv, pos_inv = parse("ENTRADA_INVALIDA", tokens, 0, grammar)
            if arbol_inv and pos_inv == len(tokens):
                print("DCG — ENTRADA INVÁLIDA detectada por CFG")
            else:
                print("DCG — falla de concordancia o estructura")

        # Ambigüedad
        patron, args = detectar_ambiguedad(tokens)
        if patron:
            print(f"AMBIGÜEDAD detectada — args={args}")
            print(patron["mensaje"].format(*args))


# ── Conversación interactiva con el mesero ────────────────────

def run_atn():
    mesero = ATNMesero()
    print("\n" + "=" * 60)
    print("  ParseBurger — Mesero Virtual (ATN)")
    print("  Escribe 'salir' para terminar")
    print("=" * 60)

    print("\nMesero:", mesero.transicion("inicio"))

    while mesero.estado != "FIN":
        try:
            entrada = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Sesión terminada]")
            break
        if entrada.lower() == "salir":
            print("Mesero: ¡Hasta pronto!")
            break
        print(f"\nMesero: {mesero.transicion(entrada)}")

    if mesero.estado == "FIN":
        print("\n[ATN alcanzó estado FIN — pedido completado]")


# ── Punto de entrada ──────────────────────────────────────────

if __name__ == "__main__":
    print("\nParseBurger — ¿Qué deseas ejecutar?")
    print("  1) Demo de casos de prueba (CFG + DCG + PCFG)")
    print("  2) Conversación interactiva con el mesero (ATN)")
    print("  3) Ambos")

    opcion = input("Opción (1/2/3): ").strip()

    if opcion == "1":
        demo_casos()
    elif opcion == "2":
        run_atn()
    elif opcion == "3":
        demo_casos()
        run_atn()
    else:
        print("Opción no válida. Ejecutando demo por defecto...")
        demo_casos()
