# Neurito 3.0: aprende a encontrar comida en un laberinto

Neurito busca comida dentro de tres laberintos. Su cerebro debe elegir entre arriba, abajo, izquierda y derecha. La red se construye con NumPy, y Pygame dibuja el escenario, la mascota y una gráfica de la pérdida.

## Cómo aprende

1. BFS calcula rutas cortas y genera ejemplos etiquetados: mapa, posición, meta y movimiento recomendado.
2. Los ejemplos se dividen en entrenamiento (80 %) y prueba (20 %). Los pares posición-meta de prueba no aparecen en entrenamiento.
3. Cada entrada incluye un vector one-hot de tres mapas y dos vectores one-hot de 81 casillas: 165 características.
4. La arquitectura es 165 → 96 → 4. Usa ReLU en la capa oculta y Softmax en las cuatro salidas.
5. El entrenamiento minimiza entropía cruzada multiclase mediante retropropagación y descenso de gradiente con mini-lotes.
6. Durante el juego, el modelo decide sin consultar BFS. BFS es el experto que proporcionó las etiquetas.

Esto es aprendizaje supervisado por imitación, NO aprendizaje por refuerzo.

## Dos modos

- Red pura: toma la salida de mayor probabilidad. Puede chocar con paredes o quedarse en ciclos.
- Asistido: descarta movimientos contra paredes y penaliza casillas visitadas. Son reglas adicionales, no conocimientos aprendidos por la red.

La precisión de clasificación no equivale al porcentaje de laberintos completados.

## Estructura

- laberinto_mundo.py: mapas, movimiento, BFS y navegación asistida.
- laberinto_red.py: red neuronal y entrenamiento con NumPy.
- laberinto.py: juego Pygame, sprites y pérdida.
- test_laberinto.py: pruebas automáticas.
- GUIA_LABERINTO.md: esta guía.

Reutiliza assets/neutral_1.png, neutral_2.png y neutral_3.png. No modifica las versiones anteriores.

## Ejecutar

    uv sync
    uv run laberinto.py

## Controles

| Tecla | Acción |
|---|---|
| 1 | Entrenar una época |
| 2 | Entrenar cien épocas |
| 3 | Entrenamiento continuo |
| A | Alternar red pura y navegación asistida |
| P | Alternar navegación automática y paso a paso |
| Espacio | Avanzar un paso en modo manual |
| N | Cambiar mapa |
| G | Nuevas posiciones y meta |
| C | Reiniciar contadores |
| R | Reiniciar pesos y entrenamiento |
| Esc | Salir |

## Probar automáticamente

    uv run python -m unittest -v test_laberinto.py

## Experimentos

1. Observa Neurito sin entrenar. ¿Por qué se atasca?
2. Entrena 100, 200 y 400 épocas. Compara pérdida, precisión y movimientos.
3. Compara red pura frente a navegación asistida. ¿Qué parte corresponde al modelo y cuál a las reglas?
4. Cambia las 96 neuronas ocultas por 16, 32 o 128.
5. Cambia la tasa de aprendizaje 0.45 y observa si converge.
6. Cambia de mapa. Los mapas forman parte del entrenamiento, pero las combinaciones de inicio y meta usadas para probar no se entrenaron.
7. Haz vibecoding para verificar como mejora o empeora Neurito al cambiar BFS, por DFS y A*

## Alcance y limitaciones

El modelo no interpreta capturas de pantalla: trabaja con características estructuradas. Conoce el identificador de cada mapa. Los tres mapas pertenecen al mismo universo de entrenamiento. La evaluación demuestra generalización a pares de posición-meta no entrenados, no a laberintos totalmente desconocidos. Para eso habría que representar también las paredes de cualquier mapa nuevo y entrenar y evaluar en mapas separados.

## Resultados de los experimentos

### 1. Neurito sin entrenar

| Exactitud de prueba | Éxito (red pura) | Pegado a una pared | Dando vueltas |
|---|---|---|---|
| 27.7 % | 3.1 % | 82.3 % | 14.7 % |

Se atasca porque sus pesos son al azar y no sabe dónde está la comida. Las cuatro probabilidades salen casi iguales (la más alta apenas llega a 30 %) y gana la que le toque por suerte: elige ARRIBA o ABAJO el 86 % de las veces, sin importar dónde esté la meta. Si ahí hay una pared, no se mueve, ve exactamente lo mismo y repite el mismo choque hasta rendirse.

### 2. Entrenar 100, 200 y 400 épocas

| Épocas | Pérdida | Exactitud entrenamiento | Exactitud prueba | Éxito red pura | Éxito asistido |
|---|---|---|---|---|---|
| 100 | 0.1352 | 94.1 % | 84.9 % | 51.3 % | 100 % |
| 200 | 0.0376 | 99.9 % | 90.1 % | 81.3 % | 100 % |
| 400 | 0.0107 | 100 % | 91.5 % | 82.7 % | 100 % |

- La pérdida baja mucho y la exactitud sube rápido hasta las 200 épocas. De 200 a 400 casi no mejora (solo 1.4 puntos).
- Con 100 épocas, casi la mitad de los intentos de la red pura (46.6 %) se quedan dando vueltas. Con 400 baja a 16.9 %.
- Cuando la red pura llega a la comida, casi siempre lo hace por el camino más corto.
- El modo asistido ya llega siempre desde las 100 épocas, pero da más rodeos: 2.1 pasos de más con 100 épocas y 0.6 con 400.

### 3. Red pura frente a navegación asistida (400 épocas)

| Quién decide | Éxito | Pasos de más |
|---|---|---|
| Solo las reglas (sin red, todas las direcciones igual de probables) | 93.0 % | 13.0 |
| Red pura | 82.7 % | 0.0 |
| Red + reglas (asistido) | 100 % | 0.6 |

- **La red** sabe hacia dónde está la comida. Por eso, cuando acierta, va directo.
- **Las reglas** descartan las paredes y penalizan las casillas ya visitadas. Eso quita los choques y los ciclos, pero no saben dónde está la comida.
- La red sola se queda dando vueltas porque decide solo con la posición y la meta, sin memoria. Si pisa una casilla por segunda vez, repite lo mismo y ya no sale.
- Las reglas solas llegan a bastante (93 %), pero explorando a ciegas, con muchos rodeos.
- Juntas se complementan. Por eso el 100 % del modo asistido no es solo mérito de la red.

### 4. Neuronas ocultas: 16, 32, 96 o 128 (400 épocas)

| Ocultas | Pérdida | Exactitud entrenamiento | Exactitud prueba | Éxito red pura | Éxito asistido |
|---|---|---|---|---|---|
| 16 | 0.0342 | 99.4 % | 87.2 % | 74.3 % | 100 % |
| 32 | 0.0161 | 100 % | 89.2 % | 78.4 % | 100 % |
| 96 | 0.0107 | 100 % | 91.5 % | 82.7 % | 100 % |
| 128 | 0.0103 | 100 % | 90.8 % | 85.3 % | 100 % |

Con 16 y 32 neuronas aprende menos. De 96 a 128 casi no cambia, y las pequeñas diferencias parecen ruido. Al repetir con 5 semillas distintas para la red, la exactitud de prueba promedio fue 88.3 %, 90.5 %, 91.1 % y 90.8 %. Con 96 neuronas alcanza.

### 5. Tasa de aprendizaje (400 épocas)

| Tasa | Pérdida final | Exactitud prueba | Éxito red pura | ¿Converge? |
|---|---|---|---|---|
| 0.01 | 0.6818 | 73.9 % | 20.4 % | muy lento, en 400 épocas no alcanza a aprender |
| 0.1 | 0.1490 | 87.2 % | 60.2 % | sí, pero más lento |
| 0.45 | 0.0107 | 91.5 % | 82.7 % | sí |
| 1.0 | 0.0028 | 93.3 % | 85.5 % | sí, más rápido |
| 2.0 | 0.0011 | 93.3 % | 85.6 % | sí, más rápido |
| 5.0 | 1.1870 | 30.3 % | 4.5 % | no |

Con 0.45 sí converge: la pérdida baja con pequeños altibajos hasta 0.01. Es una tasa segura, pero no es la mejor, porque 1.0 y 2.0 llegan más lejos en las mismas épocas. Con 5.0 se pasa: la pérdida llegó a subir hasta 1.93, termina en 1.19 y apenas acierta más que al azar (30.3 %, cuando adivinar da 25 %).

### 6. Cambiar de mapa (400 épocas)

| Mapa | Combinaciones de prueba | Exactitud entrenamiento | Exactitud prueba | Éxito red pura | Éxito asistido |
|---|---|---|---|---|---|
| 1 | 210 | 100 % | 92.4 % | 85.7 % | 100 % |
| 2 | 251 | 100 % | 90.0 % | 78.5 % | 100 % |
| 3 | 255 | 100 % | 92.2 % | 84.3 % | 100 % |

- Se comporta parecido en los tres mapas. El mapa 2 fue el que más le costó.
- En las combinaciones que vio al entrenar acierta el 100 %, y en las nuevas cerca del 91 %. Esa diferencia es lo que le falta para generalizar del todo, pero igual resuelve la mayoría de las combinaciones de inicio y meta que nunca vio.

### 7. Cambiar BFS por DFS y A\*

BFS no participa mientras Neurito juega: solo sirve para crear las etiquetas de entrenamiento, o sea, para decirle a la red cuál era el movimiento correcto. Por eso, cambiar el algoritmo significa cambiar al "profesor". Para probarlo se reemplazó solo esa parte: para cada posición y meta, el algoritmo busca un camino y su primer paso es la etiqueta. Los ejemplos, la división entre entrenamiento y prueba y la red (96 neuronas, tasa 0.45, 400 épocas) son los mismos. Lo único que cambia son las etiquetas.

| Profesor | Etiquetas distintas a BFS | Exactitud de prueba (contra sus propias etiquetas) | Movimientos óptimos | Éxito red pura | Éxito asistido | Pasos de más (asistido) |
|---|---|---|---|---|---|---|
| BFS | 0 % | 91.5 % | 93.3 % | 82.7 % | 100 % | 0.6 |
| A\* | 1.8 % | 92.6 % | 93.9 % | 86.5 % | 100 % | 0.6 |
| DFS | 49.8 % | 99.9 % | 50.4 % | 7.5 % | 44.8 % | 13.3 |

"Movimientos óptimos" es el porcentaje de veces que la red elige un movimiento que de verdad acerca a la comida por un camino más corto. Se calcula igual para los tres, por eso sirve para compararlos.

- **A\* queda casi igual que BFS.** Los dos encuentran el camino más corto. Solo cambia cuál escogen cuando hay varios caminos igual de cortos (por eso apenas el 1.8 % de las etiquetas es distinto). El 86.5 % contra 82.7 % de la red pura parece una mejora, pero al repetir con 5 semillas distintas queda en 84.5 % contra 83.4 %, o sea, es una diferencia pequeña. Aquí A\* no aporta nada, porque BFS ya calcula el camino más corto una vez por meta y lo reutiliza.
- **DFS empeora mucho a Neurito.** DFS encuentra un camino, pero no el más corto, y a veces da rodeos largos. La mitad de sus etiquetas no coinciden con las de BFS, y además salen muy desbalanceadas: 55 % ARRIBA y solo 1.8 % DERECHA, por el orden en que DFS prueba las direcciones. Ni el propio DFS, usado como jugador, llega a la comida (solo el 7.7 %).
- **La exactitud engaña.** La red aprende las etiquetas de DFS casi perfecto (99.9 %, pérdida de 0.0012), pero solo elige un movimiento bueno la mitad de las veces y llega a la comida en el 7.5 %. Las aprende bien porque el patrón es fácil, no porque entienda el laberinto.
- **Las reglas no arreglan una guía equivocada.** Con la red de DFS, el modo asistido llega al 44.8 %, mientras que las reglas solas, sin red, llegaban al 93 %. Una red que apunta mal estorba más que no tener red.

BFS es la mejor opción para este proyecto, porque el problema necesita las etiquetas del camino más corto. A\* sirve igual, y DFS no. Una limitación: las etiquetas de DFS dependen del orden en que prueba las direcciones (aquí arriba, abajo, izquierda, derecha). Con otro orden saldrían números distintos, aunque seguiría sin dar el camino más corto.
