# Horus — Alcance del MVP, Justificación y Limitaciones

> Documento de respaldo para la tesis. Encuadra el trabajo realizado como un
> **producto mínimo viable (MVP)** y documenta formalmente, con evidencia del
> dataset, los sesgos y limitaciones identificados durante el análisis
> exploratorio y el entrenamiento. Su propósito es proteger el valor del trabajo
> ya realizado: **no** propone rehacer el pipeline, sino explicitar qué se hizo,
> por qué se hizo así y qué queda para trabajo futuro.
>
> **Trazabilidad**: cada hallazgo citado aquí está medido y concluido en los
> notebooks del pipeline (secciones "Interpretación..." de `00_normalize`,
> `01_explore`, `02_features` y `03_train`). El número de celda puede variar
> según la versión; se referencia la sección por su título.

## 1. Contexto: por qué esto es un MVP

El proyecto se desarrolló bajo dos restricciones que condicionaron todas las
decisiones de alcance:

- **Tiempo**: la aprobación del proyecto exigió una versión funcional en un
  plazo de aproximadamente **3 meses**, lo que obligó a priorizar un pipeline
  completo y evaluable por encima de la sofisticación de cada etapa.
- **Hardware**: el entrenamiento se ejecutó sobre una máquina de **potencia
  limitada**, sin GPU, lo que descartó de entrada modelos profundos o basados en
  transformers y condicionó la familia de algoritmos evaluables.

En ese contexto, el entregable se definió como un **pipeline end-to-end
funcional** (normalización → EDA → features → modelado → deploy) que demostrara
la viabilidad de la detección de cyberbullying en texto con **modelos clásicos
de aprendizaje automático** sobre representaciones **TF-IDF**. El objetivo no
era lograr el mejor modelo posible, sino **evidenciar el problema, medir la
línea base y dejar el terreno preparado para modelos más potentes**.

Este documento registra las limitaciones que ese alcance implica, con el
compromiso de tratarlas como **trabajo futuro** y no como defectos ocultos.

---

## 2. Fase exploratoria: sesgos identificados en los datos

Todo lo que sigue fue medido sobre `data/processed/
cyberbullying_preprocessed.csv` (**80 974 mensajes**), el dataset intermedio
generado por la etapa de normalización (`00_normalize`). Los hallazgos quedan
concluidos en las secciones de interpretación de `01_explore` y condicionan la
lectura de cualquier métrica del modelo.

### 2.1 Desbalance de clases

La variable objetivo no está equilibrada: la clase positiva (cyberbullying)
concentra el **60.98 %** de los mensajes frente al **39.02 %** de la clase
negativa.

| Clase | Proporción |
| ----- | ---------- |
| 1 (bullying) | 60.98 % |
| 0 (no bullying) | 39.02 % |

**Implicación**: en estas condiciones la *accuracy* es una métrica engañosa —
un clasificador trivial que siempre predijera la clase mayoritaria ya acertaría
~61 % de las veces. Por eso el entrenamiento adopta métricas orientadas al
desbalance (ver sección 3). *(Concluido en `01_explore`, sección
"Interpretación de los resultados del EDA".)*

### 2.2 Sesgo por longitud de texto

Las distribuciones de longitud difieren sistemáticamente entre clases:

| Clase | Media (palabras) | Mediana | Desvío |
| ----- | ---------------- | ------- | ------ |
| 0 (no bullying) | 6.2 | 6.0 | 3.7 |
| 1 (bullying) | 10.9 | 9.0 | 6.8 |

La correlación de Pearson entre la longitud (en palabras) y la clase es de
**0.364** (0.367 en caracteres, 0.366 en tokens únicos; la riqueza léxica
correlaciona débil y negativamente, -0.148): los mensajes de bullying tienden
a ser notablemente más largos. *(Concluido en `01_explore`, secciones "la
extensión del mensaje como señal correlacionada" y "correlación de
características derivadas con la clase".)*

**Implicación doble**:

1. El modelo puede aprender a usar la **longitud como proxy de la clase** en
   lugar de aprender el *contenido* del acoso, lo que degrada su capacidad de
   generalización frente a mensajes cortos de acoso real.
2. En un enfoque TF-IDF, los textos más largos poseen más términos y por lo
   tanto más peso global en el documento, amplificando el efecto anterior.

### 2.3 Vocabulario compartido entre clases

El **32.9 % del vocabulario total es compartido** entre clases (índice de
Jaccard 0.329: 12 725 tokens compartidos de 38 713). Es decir: apenas un
tercio del vocabulario es exclusivo de una clase, y las palabras que definen
al bullying también aparecen, con otra frecuencia o contexto, en la clase
negativa. *(Concluido en `01_explore`, sección "vocabulario compartido entre
clases".)*

**Implicación**: la clasificación por presencia de términos es intrínsecamente
ruidosa. Un modelo TF-IDF decide por *presencia/frecuencia ponderada*, sin
acceso al contexto que determina si un término es acoso o no.

### 2.4 Riesgo de falsos positivos en términos de identidad

El hallazgo más sensible: las menciones a **colectivos vulnerables aparecen
desproporcionadamente etiquetadas como bullying** en el dataset. *(Concluido
en `01_explore`, sección "riesgo de falsos positivos en términos de
identidad", que cuantifica estos porcentajes sobre los textos que mencionan
cada término.)*

| Término | Textos que lo mencionan | % etiquetado como bullying |
| ------- | ----------------------- | --------------------------- |
| muslim | 3 181 | 96.4 % |
| girl | 5 526 | 92.5 % |
| gay | 4 764 | 90.7 % |
| lesbian | 152 | 96.7 % |
| trans | 122 | 93.4 % |
| woman | 3 582 | 88.0 % |

**Implicación**: un modelo entrenado sobre estos datos puede aprender que
*"mencionar una identidad" ≈ "bullying"*, generando falsos positivos cuando un
mensaje simplemente habla de, por ejemplo, una persona musulmana, gay o mujer
sin contenido de acoso. Este sesgo es un **riesgo ético de producto**: en un
sistema desplegado podría silenciar precisamente a los colectivos que el
bullying ataca. Es la limitación más importante para el trabajo futuro
(sección 5).

### 2.5 Léxico de odio presente en ambas clases

El léxico grosero/ofensivo no es exclusivo de la clase positiva: aparece en el
**28.1 %** de la clase negativa y en el **35.3 %** de la positiva. *(Concluido
en `01_explore`, sección "Interpretación de los resultados del EDA"; el
vocabulario ofensivo de ambas clases es visible en el análisis de palabras
frecuentes y n-gramas.)*

**Implicación**: la sola presencia de groserías no discrimina clases. Un
clasificador basado en diccionarios o frecuencias de términos ofensivos
generará **falsos positivos** sobre discurso duro pero no abusivo, y falsos
negativos sobre acoso implícito/sutil.

---

## 3. Fase de entrenamiento: decisiones tomadas frente al desbalance

El modelado (`notebooks/03_train.ipynb`) incorporó explícitamente las
mitigaciones derivadas de los hallazgos exploratorios:

- **Métricas orientadas al desbalance**: la selección de modelo y la validación
  se hacen sobre **F1-Score**, no sobre accuracy, penalizando los clasificadores
  que "ganan" solo por explotar la clase mayoritaria.
- **Validación cruzada (CV = 5)**: cada pipeline completo
  (`TfidfVectorizer` + clasificador) se evalúa con validación cruzada de 5
  pliegues sobre la partición de entrenamiento, reduciendo la varianza de la
  estimación; por costo, se aplica a los 3 mejores modelos por F1.
- **Partición estratificada** (80/20, 64 779 / 16 195): la proporción de clases
  se preserva en train/test para que la evaluación no dependa del azar del
  muestreo.
- **Umbral de decisión explícito** en 0.5 sobre la clase positiva, para que el
  comportamiento de clasificación sea reproducible y auditable.

Se entrenan **7 clasificadores** con pipeline `TfidfVectorizer + clasificador`.
Resultados obtenidos (F1 sobre el conjunto de test, `data/output/
models_results.csv`, y CV en `03_train`):

| Modelo | Precision | Recall | F1 (test) |
| ------ | --------- | ------ | --------- |
| Random Forest | 0.836 | 0.829 | **0.833** |
| SVM (kernel lineal) | 0.854 | 0.777 | 0.814 |
| Logistic Regression | 0.847 | 0.781 | 0.813 |
| Neural Network (MLP) | 0.874 | 0.757 | 0.811 |
| Multinomial Naive Bayes | 0.736 | 0.888 | 0.805 |
| XGBoost | 0.905 | 0.712 | 0.797 |
| Gradient Boosting | 0.911 | 0.682 | 0.780 |

La CV confirma la jerarquía (Random Forest F1 media 0.828, SVM lineal 0.812,
Regresión Logística 0.811, con desvíos ±0.003). *(Concluido en `03_train`,
sección "Interpretación de los resultados".)*

**Lectura honesta del resultado**: un F1 ≈ 0.83 es un resultado razonable para
la línea base de un MVP, pero convive con los sesgos de la sección 2. En
particular, el patrón precision/recall de los modelos sugiere que parte del
"acierto" se apoya en señales correlacionadas (longitud, presencia de términos
ofensivos, menciones de identidad) más que en comprensión del acoso.

---

## 4. Limitaciones del enfoque léxico (TF-IDF)

Las limitaciones observadas en las secciones 2.3–2.5 no son defectos de
implementación: son **límites estructurales del paradigma léxico**. Son la
evidencia de por qué las soluciones tradicionales basadas en frecuencia se
quedan cortas:

1. **Sin orden ni contexto**: TF-IDF representa cada texto como un saco de
   términos ponderados. "te odio" y "no te odio" comparten los mismos tokens y
   difieren solo en un marcador de negación que el modelo clásico debe aprender
   a ponderar por frecuencia, no por significado. (En `01_explore` se verificó
   además que la negación no aparece entre los n-gramas frecuentes y que su
   poder separador es limitado.)
2. **Sensibilidad al vocabulario compartido**: el 32.9 % del vocabulario es
   compartido (2.3) y el léxico ofensivo aparece en ambas clases (2.5), por lo
   que la frontera de decisión es necesariamente borrosa.
3. **Señales correlacionadas confundidas con causa**: el modelo no distingue
   entre "menciona una identidad" y "ataca una identidad" (2.4), ni entre
   "texto largo" y "texto abusivo" (2.2). Aprende correlaciones estadísticas,
   no intención. En `02_features` se observa el mecanismo: los términos de
   identidad y ofensa tienen IDF altos y ganan peso desproporcionado cuando
   aparecen, amplificando el sesgo de la etiqueta.
4. **Cero generalización semántica**: no hay forma de que un modelo léxico
   reconozca acoso expresado con palabras que no aparecieron (o que aparecieron
   poco) en el entrenamiento. Además, los filtros de frecuencia usados en la
   inspección de `02_features` descartan la mayor parte del vocabulario
   (38 713 → 118 términos), incluyendo vocabulario potencialmente
   discriminante.

Estas cuatro propiedades son el argumento estructural de por qué el **siguiente
salto** del proyecto pasa por modelos contextuales (sección 5).

---

## 5. Trabajo futuro

El análisis de este documento define la agenda, priorizada por impacto:

1. **Modelos contextuales (transformers)** — la línea de trabajo que el
   paradigma léxico no puede cubrir (sección 4): representaciones dependientes
   del contexto (por ejemplo, arquitecturas tipo BERT y sus variantes
   eficientes para hardware limitado) para distinguir significado real de
   presencia de términos. Requiere evaluación de viabilidad computacional.
2. **Mitigación del sesgo identitario (2.4)** — la prioridad ética: detección y
   corrección del sesgo que asocia menciones de identidad con acoso, ya sea con
   datos balanceados, técnicas de *fairness* o supervisión explícita.
3. **Re-balanceo de clases (2.1)** — evaluar *class weights*, sub/sobre-muestreo
   o técnicas sintéticas manteniendo las métricas orientadas al desbalance ya
   adoptadas.
4. **Control del sesgo por longitud (2.2)** — análisis de sensibilidad del
   modelo frente a la longitud y estrategias (normalización, features
   independientes de la extensión) para desacoplarla de la clase.
5. **Léxico y datos (2.5)** — ampliación del corpus con discurso duro no
   abusivo y acoso implícito, para reducir falsos positivos y negativos.
6. **Duplicados** — el 43.09 % de las filas comparten texto; una deduplicación
   antes de particionar evitaría que un mismo mensaje aparezca en train y test
   y sobreestime las métricas.

---

## 6. Conclusión

El MVP entrega un pipeline completo, evaluado con métricas apropiadas al
desbalance (F1 + validación cruzada) y desplegable, dentro de las restricciones
de tiempo y hardware del proyecto. Los sesgos documentados en este informe no se
ocultan: se miden, se explican y se convierten en la hoja de ruta del trabajo
futuro. En particular, el análisis de las limitaciones del enfoque TF-IDF
fundamenta — con evidencia del propio dataset — por qué las soluciones léxicas
basadas en frecuencia se quedan cortas frente a los modelos contextuales, que
son la dirección natural de evolución del proyecto.
