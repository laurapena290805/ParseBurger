# 🍔 ParseBurger

Sistema de procesamiento de lenguaje natural para pedidos de hamburguesas. Combina una gramática libre de contexto (CFG), una gramática de cláusulas definidas (DCG) con unificación de rasgos morfológicos, detección de ambigüedad sintáctica con resolución PCFG, y un autómata de transiciones de red (ATN) que implementa un mesero virtual interactivo.

---

## Requisitos

- Python 3.8 o superior
- No requiere librerías externas (solo módulos de la biblioteca estándar)

---

## Cómo ejecutar

```bash
python main.py
```

Al iniciar, el sistema presentará tres opciones:

```
ParseBurger — ¿Qué deseas ejecutar?
  1) Demo de casos de prueba (CFG + DCG + PCFG)
  2) Conversación interactiva con el mesero (ATN)
  3) Ambos
```

### Opción 1 — Demo

Ejecuta automáticamente 8 casos de prueba predefinidos que cubren todos los escenarios del sistema: pedidos válidos, ambigüedad sintáctica, entradas inválidas, fallos de concordancia y visualización del árbol de derivación.

### Opción 2 — Mesero virtual

Abre una conversación interactiva. Ejemplos de pedidos que puedes escribir:

```
quiero dos hamburguesas sin cebolla con queso
dame una clasica sin tomate y lechuga
quisiera tres especiales con extra tocino
ponme una vegana con mucho ketchup
```

Escribe `salir` para terminar la sesión.

---

## Estructura del proyecto

```
parseburger/
├── main.py          # Punto de entrada
├── gramatica.py     # Gramática CFG
├── parser.py        # Parser recursivo descendente + árbol de derivación
├── lexico.py        # Léxico DCG con rasgos morfológicos y unificación
├── tokenizador.py   # Normalización y tokenización del texto de entrada
├── ambiguedad.py    # Detección de ambigüedad + PCFG
├── atn_mesero.py    # ATN del mesero virtual (diálogo)
└── README.md
```

---

## Descripción de cada módulo

### `gramatica.py` — Gramática CFG

Define la gramática libre de contexto del sistema como un diccionario de Python. Contiene únicamente reglas estructurales; el vocabulario y sus rasgos viven en `lexico.py`.

Reglas principales:

| Símbolo | Descripción |
|---|---|
| `PEDIDO` | Raíz de un pedido válido: verbo + sintagma nominal |
| `NP_PEDIDO` | Sintagma nominal: cantidad + producto (+ modificadores opcionales) |
| `VERBO_PEDIR` | `quiero`, `dame`, `quisiera`, `ponme` |
| `CANTIDAD` | `un`, `una`, `dos`, `tres`, `cuatro`, `cinco` |
| `PRODUCTO` | Tipo de hamburguesa, simple o compuesta (`hamburguesa clasica`) |
| `MOD_LIST` | Lista de modificadores encadenados |
| `MOD` | Un modificador: `sin`/`con`/`extra` + ingrediente |
| `ENTRADA_INVALIDA` | Ítem fuera del menú (`pizza`, `hotdog`, etc.) |

La regla `MOD_LIST_TAIL` introduce **ambigüedad intencional** para el caso `sin X y Y`, que el módulo de ambigüedad resuelve.

---

### `parser.py` — Parser recursivo descendente

Implementa dos funciones sobre la gramática CFG:

- **`parse(simbolo, tokens, pos, gram)`** — retorna el primer árbol de derivación válido `(Nodo, posición_final)` o `(None, pos)` si falla. Utilizado para reconocimiento rápido.
- **`parse_todos(simbolo, tokens, pos, gram)`** — retorna *todos* los árboles posibles. Si `len(resultado) > 1`, se ha detectado ambigüedad estructural.

La clase **`Nodo`** representa el árbol de derivación. El método `mostrar()` imprime el árbol con sangría por nivel:

```
PEDIDO
  VERBO_PEDIR
    quiero
  NP_PEDIDO
    CANTIDAD
      dos
    PRODUCTO
      ...
```

---

### `lexico.py` — Léxico DCG con unificación de rasgos

Contiene el diccionario `lexico_dcg` con los rasgos morfológicos de cada palabra (categoría, número, género). Implementa:

- **`unificar(dag1, dag2)`** — algoritmo de unificación de DAGs de rasgos. Retorna el DAG combinado o `None` ante conflicto.
- **`dcg_parse_pedido(tokens)`** — verifica la concordancia de género y número entre la cantidad y el producto usando la tabla `CONCORDANCIA_GEN` y unificación directa. Retorna un diccionario semántico del pedido o `None` si hay fallo de concordancia.

Ejemplos de concordancia:

| Entrada | Resultado |
|---|---|
| `quiero dos hamburguesas` | ✅ `neu` + `fem` permitido |
| `dame una clasica` | ✅ `fem` + `fem` |
| `quiero un hamburguesas` | ❌ `sg` ≠ `pl` |
| `dame una doble` | ❌ `fem` + `masc` no permitido |

---

### `tokenizador.py` — Tokenizador

Normaliza el texto del usuario antes de pasarlo al parser:

1. Convierte a minúsculas y elimina puntuación.
2. Reemplaza frases multi-palabra (`perro caliente` → `perro_caliente`).
3. Elimina tildes (`clásica` → `clasica`).
4. Filtra palabras funcionales irrelevantes (`por`, `favor`, `me`).

---

### `ambiguedad.py` — Detección de ambigüedad y PCFG

Maneja dos tipos de ambigüedad:

**Ambigüedad léxica por patrón** — `detectar_ambiguedad(tokens)` busca el patrón `sin <ING> y <ING>` en los tokens. Cuando lo encuentra, retorna el patrón y los argumentos para que el ATN solicite al usuario que elija entre:
- Opción A: `sin {X} y sin {Y}` — excluir ambos ingredientes
- Opción B: `sin {X}, pero con {Y}` — excluir solo el primero

**Ambigüedad estructural con PCFG** — cuando `parse_todos` devuelve más de un árbol válido, el sistema usa probabilidades por producción (`PCFG_PROBS`) para seleccionar el árbol más probable:
- `pcfg_score(arbol)` — calcula la probabilidad multiplicando las probabilidades de cada producción usada.
- `mejor_arbol_pcfg(arboles)` — retorna el árbol con mayor score.

---

### `atn_mesero.py` — ATN del mesero virtual

Implementa un **Autómata de Transiciones de Red (ATN)** de diálogo con cinco estados:

```
INICIO → ESCUCHANDO ⇄ AMBIGUO
                  ↓
             CONFIRMANDO → FIN
                  ↑ (cancelar)
```

La tabla de transiciones `DIALOGO_ATN` centraliza todos los arcos. Las **subredes** analizan la entrada y devuelven un arco; el **motor** consulta la tabla y actualiza el estado:

| Estado | Función | Descripción |
|---|---|---|
| `INICIO` | `_subred_inicio()` | Saluda y muestra el menú |
| `ESCUCHANDO` | `_subred_escuchando()` | Analiza el pedido con CFG + DCG, detecta ambigüedad |
| `AMBIGUO` | `_subred_ambiguo()` | Espera que el usuario elija A o B |
| `CONFIRMANDO` | `_subred_confirmando()` | Muestra resumen y espera confirmación |
| `FIN` | — | Pedido cerrado |

La subred `ESCUCHANDO` aplica los módulos en este orden:
1. Detecta entradas inválidas (ítem fuera del menú) con CFG.
2. Detecta ambigüedad léxica por patrón.
3. Parsea todos los árboles CFG; si hay varios, aplica PCFG.
4. Verifica concordancia morfológica con DCG.

---

## Flujo general del sistema

```
Texto usuario
      │
      ▼
 tokenizador.py  ──── normalización y tokenización
      │
      ▼
 gramatica.py + parser.py  ──── análisis CFG (árbol de derivación)
      │
      ├── ambiguedad.py  ──── detección de patrón "sin X y Y"
      │                       resolución PCFG si hay >1 árbol
      │
      ▼
 lexico.py  ──── verificación DCG (concordancia género/número)
      │
      ▼
 atn_mesero.py  ──── gestión del diálogo y respuesta al usuario
```

---

## Casos de prueba cubiertos

| Caso | Descripción |
|---|---|
| Pedido válido con modificadores | `quiero dos hamburguesas sin cebolla pero con extra queso` |
| Ambigüedad sintáctica | `dame una clasica sin tomate y lechuga` → solicita A o B |
| Entrada inválida | `quiero un perro_caliente` → rechazado por CFG |
| Fallo de concordancia (número) | `quiero un hamburguesas` → rechazado por DCG |
| Fallo de concordancia (género) | `dame una doble` → rechazado por DCG |
| Pedido con extra | `ponme una especial con extra tocino sin mayonesa` |
| Múltiples árboles + PCFG | Selección automática del árbol más probable |
| Árbol de derivación visible | Impresión del árbol completo |