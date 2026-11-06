# Experimentos de Neurito 2.0 (salto)

## 1. Juego sin entrenar

| Precisión de prueba | Saltos | Esquivados | Choques |
|---|---|---|---|
| 44.9 % | 0 | 0 | 20 |

Neurito nunca salta, así que choca con todo. Los 20 choques son casi el mismo, porque después de cada choque la pista se reinicia con la misma velocidad (5.5) y vuelve a pasar lo mismo.

## 2. Entrenar de 100 en 100 épocas

| Épocas | Pérdida | Precisión | Esquivados | Choques |
|---|---|---|---|---|
| 100 | 0.2601 | 91.2 % | 22 | 1 |
| 200 | 0.2306 | 91.9 % | 24 | 0 |
| 500 | 0.1368 | 94.1 % | 24 | 0 |
| 1000 | 0.0574 | 97.8 % | 24 | 0 |

La pérdida baja siempre y la precisión sube. Pero el comportamiento ya era perfecto desde las 200 épocas. Después de eso, que la precisión pasara de 92 % a 98 % no cambió nada en el juego. Con solo 100 épocas todavía chocó una vez.

## 3. Neuronas ocultas (3, 12 o 24)

| Ocultas | Épocas | Pérdida | Prec. entrenamiento | Prec. prueba | Esquivados / Choques |
|---|---|---|---|---|---|
| 3 | 100 | 0.2649 | 90.9 % | 90.3 % | 19 / 3 |
| 3 | 1000 | 0.2060 | 93.7 % | 93.2 % | 24 / 0 |
| 12 | 100 | 0.2601 | 91.5 % | 91.2 % | 22 / 1 |
| 12 | 1000 | 0.0574 | 98.0 % | 97.8 % | 24 / 0 |
| 24 | 100 | 0.2629 | 91.1 % | 90.8 % | 22 / 1 |
| 24 | 1000 | 0.0502 | 98.3 % | 97.7 % | 24 / 0 |

- **Generalización:** en todos los casos la precisión de entrenamiento y la de prueba quedan a menos de un punto. La red no memoriza. Tiene sentido, porque los datos de prueba salen de la misma regla que los de entrenamiento.
- Con **3 neuronas** aprende menos (93.2 %), pero igual esquiva todo a las 1000 épocas.
- **24 neuronas** no mejoran a las 12. Con 12 alcanza.

## 4. Tasa de aprendizaje (0.8, 0.01 o 1.2)

| Tasa | Pérdida en la época 1 / 10 / 100 / 1000 | Prec. a las 1000 épocas | Esquivados / Choques (1000 épocas) |
|---|---|---|---|
| 0.8 | 0.710 / 0.472 / 0.260 / 0.057 | 97.8 % | 24 / 0 |
| 0.01 | 0.710 / 0.702 / 0.645 / 0.430 | 86.5 % | 0 / 18 |
| 1.2 | 0.710 / 0.420 / 0.256 / 0.039 | 98.3 % | 24 / 0 |

- **0.8:** la pérdida baja de forma pareja, sin subidas.
- **0.01:** es muy lenta. Después de 1000 épocas la pérdida todavía está en 0.43. Además, entre las 100 y las 1000 épocas la precisión bajó (de 90.7 % a 86.5 %) aunque la pérdida siguió bajando. A las 1000 épocas no esquiva nada.
- **1.2:** es la que más baja la pérdida, pero se nota más movida: en 1000 épocas la pérdida subió 292 veces (poquito, y luego volvía a bajar). Terminó bien, así que con 1.2 todavía no se vuelve inestable.

---

## Pregunta central: ¿por qué clasifica bien y aun así choca?

La precisión mide si la decisión coincide con la etiqueta en ejemplos sueltos. En el juego, **un solo salto mal hecho ya es un choque**.

Al mirar en qué se equivoca la red de 100 épocas (132 errores en 1500 ejemplos de prueba). Todos son de **saltar de más**: nunca se queda quieta cuando debía saltar. Unos 90 son con el obstáculo ya casi encima y 39 son entre 13 y 16 fotogramas antes. Estos últimos son los peligrosos, porque en el juego Neurito salta apenas la red dice que sí, o sea, salta demasiado temprano.

Con los obstáculos lentos eso es grave, porque el margen es angosto. Con velocidad 4.5, el salto sirve si se hace entre 4 y 14.5 fotogramas antes de llegar. Si salta más pronto, Neurito aterriza encima del obstáculo.

| Red | Precisión | Salta con ... fotogramas de anticipación | Resultado con el obstáculo lento |
|---|---|---|---|
| 12 ocultas, 100 épocas | 91.2 % | 16.7 | choca |
| 12 ocultas, 1000 épocas | 97.8 % | 14.1 | esquiva |
| tasa 0.01, 100 épocas | 90.7 % | 20.1 | choca |
| 3 ocultas, 100 épocas | 90.3 % | 17.9 | choca |

Las redes de 90 % fallan con los obstáculos lentos (velocidades entre 4.5 y 5.25, según la red). La de 97.8 % salta a 14.1, justo dentro del margen, y no choca. Además, esos fallos no son de vez en cuando: pasan siempre a esas velocidades. Y como después de un choque la pista reinicia a 5.5, el mismo fallo puede repetirse una y otra vez.
