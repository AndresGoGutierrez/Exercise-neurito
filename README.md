# Exercise-neurito

Taller sobre Neurito, una red neuronal pequeña (3 entradas, 6 neuronas ocultas, 3 salidas) que decide si la mascota come, duerme o juega según su hambre, energía y aburrimiento.

Para los experimentos usé el mismo entrenamiento de `main.py` (semilla 42, 3000 ejemplos, 1200 épocas, tasa 0.1, 6 neuronas) Esta dentro de un archivo aparte, `experimentos.py`, para no tocar `main.py`. Se ejecuta con:

```
python experimentos.py

```

## Experimentos

### 1. Dos necesidades fijas, una cambia

La regla con la que se crean los datos compara tres valores: hambre, cansancio (1 - energía) y aburrimiento. Gana el más alto.

**Varía el hambre** (energía 0.5, aburrimiento 0.3):

| Hambre | Acción | Comer / Dormir / Jugar |
|---|---|---|
| 0.3 | dormir | 2 % / 96 % / 2 % |
| 0.4 | dormir | 13 % / 85 % / 2 % |
| 0.5 | comer | 50 % / 49 % / 1 % |
| 0.7 | comer | 98 % / 2 % / 0 % |

La acción cambia cuando el hambre llega a 0.5, que es justo el cansancio (1 - 0.5). Ahí se igualan.

**Varía la energía** (hambre 0.3, aburrimiento 0.3): duerme mientras la energía sea 0.6 o menos. Desde 0.7 pasa a comer, porque el cansancio baja a 0.3 y ya no gana.

**Varía el aburrimiento** (hambre 0.3, energía 0.8): come hasta 0.3 y desde 0.4 pasa a jugar.

En los tres casos el cambio ocurre cuando la necesidad que sube alcanza a la que iba ganando.

### 2. Prioridades casi iguales

Hambre en 0.70 y cansancio en 0.20, y fui subiendo el aburrimiento:

| Aburrimiento | Acción | Comer / Jugar |
|---|---|---|
| 0.40 | comer | 99.7 % / 0.3 % |
| 0.60 | comer | 88.1 % / 11.9 % |
| 0.69 | comer | 56.3 % / 43.7 % |
| 0.70 | comer | 51.5 % / 48.5 % |
| 0.71 | jugar | 46.6 % / 53.4 % |
| 0.90 | jugar | 2.3 % / 97.7 % |

Cuando las dos prioridades están lejos, Softmax da una probabilidad casi de 100 % a una. Cuando están casi iguales, las probabilidades se acercan a 50 / 50 y la acción puede cambiar por una diferencia de 0.01. Si las tres prioridades son iguales (0.5, 0.5, 0.5) sale algo parecido a 35 % / 33 % / 31 %: la red no sabe qué elegir y lo muestra.

### 3. Tamaño de la capa oculta

| Neuronas | Pérdida | Precisión |
|---|---|---|
| 3 | 0.1618 | 96.30 % |
| 6 | 0.1225 | 99.40 % |
| 10 | 0.1262 | 99.30 % |
| 20 | 0.1220 | 98.80 % |

Con 3 neuronas rinde peor, le falta capacidad. De 6 en adelante casi no mejora. Con 10 y 20 el resultado es igual o un poco peor. Para un problema tan simple, 6 neuronas alcanzan.

### 4. Épocas y tasa de aprendizaje

**Épocas** (tasa 0.1):

| Épocas | Pérdida | Precisión |
|---|---|---|
| 50 | 0.9388 | 60.60 % |
| 200 | 0.4984 | 91.80 % |
| 600 | 0.1944 | 98.60 % |
| 1200 | 0.1225 | 99.40 % |
| 3000 | 0.0711 | 99.50 % |

Mejora todo el tiempo, pero cada vez menos. De 1200 a 3000 épocas la precisión sube solo 0.1 puntos. Más épocas no dañan, simplemente ya no valen la pena.

**Tasa de aprendizaje** (1200 épocas):

| Tasa | Pérdida | Precisión | Qué pasó |
|---|---|---|---|
| 0.001 | 1.0333 | 41.80 % | casi no aprende, es muy lenta |
| 0.01 | 0.7376 | 82.90 % | aprende, pero le faltan épocas |
| 0.1 | 0.1225 | 99.40 % | bien |
| 1.0 | 0.0447 | 98.70 % | aprende rápido y baja más la pérdida |
| 5.0 | 1.0979 | 33.80 % | inestable, la pérdida llegó a subir a 4.6 y no se recuperó |
| 20.0 | 6.1621 | 33.80 % | inestable, la pérdida se disparó hasta 9.8 y terminó en 6.2 |

Con tasas muy pequeñas se queda corto, con tasas muy grandes se vuelve inestable.

### 5. ¿Qué haría falta para una cuarta acción?

Para implementar la nueva acción "Bañarse". Se necesitaría:

- **Datos:** si depende de algo nuevo, como la suciedad, una cuarta entrada. Los ejemplos pasarían de 3 columnas a 4.
- **Etiquetas:** una regla o criterio que diga cuándo la acción correcta es bañarse (por ejemplo, que la suciedad sea la prioridad más alta). Cada ejemplo necesita su etiqueta 0, 1, 2 o 3, y conviene que haya una cantidad parecida de cada una.
- **Cambios en la red:** `W1` pasa a ser 4x6 y `W2` y `b2` pasan a tener 4 salidas.
- **Cambios en el código y la interfaz:** agregar la acción en `actions`, el texto en `TEXT`, sus imágenes en `assets`, una barra o tecla para la nueva necesidad, y revisar la regla del estado "neutral".
- **Datos de prueba** nuevos, también con las 4 acciones.

Y hay que volver a entrenar, porque la red actual no sirve para esto.


## Resultados

**¿En qué se diferencian pesos y sesgos?**
Los pesos multiplican cada entrada y dicen cuánta importancia tiene. El sesgo es un número que se suma al final, no depende de las entradas y sirve para mover el punto en que la neurona se activa. En el código, `W1` y `W2` son pesos y `b1` y `b2` son sesgos.

**¿Por qué el cansancio es 1 - energía?**
Porque la energía y las otras dos necesidades van al revés. Cuando el hambre o el aburrimiento suben, hay más ganas de actuar. Pero cuando la energía sube, hay menos necesidad de dormir. Al hacer 1 - energía, las tres quedan en la misma escala: mientras más alto, más urgente, y se pueden comparar.

**¿Qué hace ReLU y qué hace Softmax?**
ReLU deja pasar los números positivos tal cual y convierte los negativos en 0 (`max(0, x)`). Se usa en la capa oculta para que la red pueda aprender cosas que no son simples líneas rectas. Softmax se usa al final: convierte las 3 salidas en probabilidades que suman 100 %. Por eso la pantalla muestra porcentajes y se escoge la más alta.

**¿Por qué una precisión alta puede ser engañosa?**
Por varias razones que se vieron en el proyecto:

- Solo cuenta aciertos, no qué tan seguro estaba. De 1000 pruebas la red falló 6, y en esas su confianza promedio fue de 51 %, contra 90 % en las que acertó. Los 6 errores fueron en casos casi empatados, y no se ven en un 99.4 %.
- La precisión se mide contra la misma regla inventada que se usó para crear los datos. Un 99.4 % solo dice que la red copió bien esa regla, no que entienda lo que necesita una mascota de verdad.
- Depende de cómo estén repartidas las clases. Aquí están parejas (34 / 32 / 34 %), así que adivinar da más o menos 34 %. Pero si una acción fuera el 90 % de los datos, una red que siempre diga esa acción tendría 90 % y no habría aprendido nada.
- La precisión y la pérdida no siempre van juntas. Con tasa 1.0 la pérdida fue más baja (0.0447) que con 0.1 (0.1225), pero la precisión fue más baja (98.7 % contra 99.4 %).
