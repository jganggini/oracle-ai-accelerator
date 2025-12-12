# Módulo 2: Fundamentos de Machine Learning

## 📋 Información del Módulo

**Peso en el examen:** 15%  
**Conceptos evaluados:**
- Fundamentos básicos de Machine Learning
- Aprendizaje Supervisado (Regresión y Clasificación)
- Aprendizaje No Supervisado
- Aprendizaje por Refuerzo

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Explicar qué es Machine Learning y cómo funciona
2. Comprender el aprendizaje supervisado (regresión y clasificación)
3. Entender el aprendizaje no supervisado y clustering
4. Conocer los fundamentos del aprendizaje por refuerzo
5. Identificar aplicaciones prácticas de cada tipo

---

## 1. ¿Qué es Machine Learning?

### Definición
**Machine Learning (ML)** es un subconjunto de Inteligencia Artificial que se enfoca en crear sistemas informáticos que pueden **aprender y predecir resultados** a partir de ejemplos, sin ser explícitamente programados.

### Analogía Simple
Imagina que quieres enseñarle a un niño a diferenciar entre perros y gatos:

**Método tradicional (programación):**
```
SI tiene_bigotes Y tiene_orejas_puntiagudas Y maúlla
  ENTONCES es_gato
SI tiene_cola_larga Y ladra
  ENTONCES es_perro
```

**Método con Machine Learning:**
- Le muestras 1,000 fotos de perros etiquetadas como "perro"
- Le muestras 1,000 fotos de gatos etiquetadas como "gato"
- El sistema aprende por sí mismo las características distintivas
- Puede identificar nuevas fotos que nunca ha visto

---

## 2. Ejemplos de ML en la Vida Diaria

| Aplicación | Cómo funciona |
|------------|---------------|
| **Compras online** 🛒 | Recomienda productos basándose en tu historial |
| **Netflix** 📺 | Sugiere películas según tus preferencias y usuarios similares |
| **Email** 📧 | Clasifica correos como spam automáticamente |
| **Autos autónomos** 🚗 | Toman decisiones de conducción basadas en datos |

---

## 3. ¿Cómo Funciona Machine Learning?

### Proceso General

```
┌─────────────┐
│ Datos de    │
│ Entrada     │ → [Features: color, tamaño, textura]
│ (Perros y   │
│  Gatos)     │
└─────────────┘
       ↓
┌──────────────────┐
│ Modelo ML        │ ← Algoritmo de aprendizaje
│ (Entrenamiento)  │
└──────────────────┘
       ↓
┌──────────────────┐
│ Modelo           │
│ Entrenado        │
└──────────────────┘
       ↓
┌──────────────────┐
│ Nueva imagen  → │ → Predicción: "Gato" o "Perro"
└──────────────────┘
```

### Componentes Clave

1. **Features (Características):** Atributos que describen los datos
   - Ejemplo: color del cuerpo, textura, color de ojos

2. **Labels (Etiquetas):** Resultado esperado
   - Ejemplo: "Perro" o "Gato"

3. **Training Data (Datos de entrenamiento):** Conjunto de features + labels

4. **Model (Modelo):** El "cerebro" que aprende patrones

5. **Inference (Inferencia):** Usar el modelo entrenado para predecir

---

## 4. Tipos de Machine Learning

### Resumen Visual

```
Machine Learning
    ├── Supervised Learning (Datos etiquetados)
    │   ├── Regression (salida continua)
    │   └── Classification (salida categórica)
    │
    ├── Unsupervised Learning (Sin etiquetas)
    │   ├── Clustering
    │   └── Dimensionality Reduction
    │
    └── Reinforcement Learning (Aprender por recompensas)
```

---

## 5. Aprendizaje Supervisado - Regresión

### ¿Qué es Regresión?
**Regresión** predice un **valor numérico continuo**.

### Ejemplo: Predicción de Precio de Casa

**Problema:**
Queremos predecir el precio de una casa basándonos en su tamaño.

**Datos de entrenamiento:**

| Tamaño (pies²) | Precio ($) |
|----------------|-----------|
| 1,000 | 200,000 |
| 1,500 | 300,000 |
| 2,000 | 400,000 |
| 2,500 | 500,000 |

**Gráfica:**

```
Precio ($)
    │
500k│                    ●
    │               ●
400k│          ●
    │     ●
300k│  ●
    │
    └────────────────────────
      1k   1.5k   2k   2.5k
           Tamaño (pies²)
```

### Regresión Lineal

La **regresión lineal** encuentra la mejor línea recta que pasa por los puntos.

**Ecuación:**
```
f(x) = w × x + b
```

Donde:
- `f(x)` = Precio predicho
- `w` = Pendiente (peso/weight)
- `x` = Tamaño de la casa
- `b` = Intercepto (bias)

**Ejemplo práctico:**
```
f(x) = 200 × x + 0

Para una casa de 1,100 pies²:
f(1.1) = 200 × 1.1 = 220,000 dólares
```

### Función de Pérdida (Loss Function)

**¿Cómo sabemos si nuestra predicción es buena?**

Calculamos el **error** entre el valor real y el predicho:

```
Loss = (Predicción - Valor Real)²
```

**Objetivo:** Ajustar `w` y `b` para minimizar el Loss.

---

### Aplicaciones de Regresión

| Aplicación | Input | Output |
|------------|-------|--------|
| Predicción de precio de casa | Tamaño, ubicación, habitaciones | Precio |
| Predicción del clima | Temperatura histórica, presión | Temperatura futura |
| Predicción de acciones | Datos históricos del mercado | Precio de acción |

---

## 6. Aprendizaje Supervisado - Clasificación

### ¿Qué es Clasificación?
**Clasificación** predice una **categoría o clase**.

### Tipos de Clasificación

1. **Clasificación Binaria:** 2 clases
   - Ejemplo: Spam o No Spam

2. **Clasificación Multi-clase:** 3+ clases
   - Ejemplo: Sentimiento (Positivo, Negativo, Neutral)

---

### Regresión Logística (Clasificación Binaria)

A pesar del nombre "regresión", **Regresión Logística** se usa para clasificación.

**Ejemplo: Aprobar o Reprobar un Examen**

**Datos:**

| Horas de Estudio | Resultado |
|------------------|-----------|
| 1 | Reprobado |
| 2 | Reprobado |
| 3 | Reprobado |
| 4 | Aprobado |
| 5 | Aprobado |
| 6 | Aprobado |

**Función Sigmoid:**

La regresión logística usa la función **sigmoid** (forma de S):

```
      Probabilidad
        │
     1.0│         ────────
        │       ╱
     0.5│     ╱
        │   ╱
     0.0│──
        └────────────────
           Horas de Estudio
```

**Características:**
- Salida entre 0 y 1 (probabilidad)
- Umbral = 0.5
  - Si P > 0.5 → Aprobado
  - Si P < 0.5 → Reprobado

**Ejemplo:**
```
Estudiante estudia 6 horas → P = 0.8 → Aprobado ✅
Estudiante estudia 2 horas → P = 0.2 → Reprobado ❌
```

---

### Clasificación Multi-clase: Flores Iris

**Dataset Iris:**
- 150 instancias de 3 tipos de flores
  - Iris-setosa
  - Iris-versicolor
  - Iris-virginica

**Features (4 características):**
1. Longitud del sépalo
2. Ancho del sépalo
3. Longitud del pétalo
4. Ancho del pétalo

**Proceso:**
```
Input: [5.1, 3.5, 1.4, 0.2]
         ↓
   Modelo entrenado
         ↓
Output: Iris-setosa
```

---

## 7. Proceso de Machine Learning en Detalle

### 7.1 Carga de Datos

```python
# Ejemplo conceptual
datos = cargar_csv("iris.csv")
```

**Salida:**
```
| sepal_length | sepal_width | petal_length | petal_width | species |
|--------------|-------------|--------------|-------------|---------|
| 5.1          | 3.5         | 1.4          | 0.2         | setosa  |
| 4.9          | 3.0         | 1.4          | 0.2         | setosa  |
```

---

### 7.2 Dividir Datos en Features (X) y Labels (y)

```
X (Features) = columnas de características
y (Labels) = columna de especies
```

---

### 7.3 Estandarización

**¿Por qué estandarizar?**

Imagina predecir el precio de una casa con:
- Tamaño: 1,000 - 5,000 pies²
- Habitaciones: 1 - 6

Sin estandarización, el modelo podría dar más peso al tamaño porque tiene valores más grandes.

**Estandarización:** Transforma datos para que tengan:
- Media = 0
- Desviación estándar = 1

**Fórmula:**
```
valor_estandarizado = (valor - media) / desviación_estándar
```

---

### 7.4 División Train/Test

**¿Por qué dividir los datos?**

Para evaluar si el modelo funciona con datos que **nunca ha visto**.

```
Datos Completos (100%)
    ↓
┌──────────────┬──────────┐
│ Train (70%)  │ Test (30%)│
└──────────────┴──────────┘
```

**Train:** Entrenar el modelo  
**Test:** Evaluar qué tan bien funciona

---

### 7.5 Entrenamiento del Modelo

```
modelo.fit(X_train, y_train)
```

El modelo **aprende** la relación entre features y labels.

---

### 7.6 Evaluación con Accuracy Score

**Accuracy (Exactitud):**
```
Accuracy = Predicciones Correctas / Total de Predicciones
```

**Ejemplo:**
- Total de muestras: 100
- Predicciones correctas: 95
- Accuracy = 95/100 = 0.95 o **95%**

---

### 7.7 Predicción con Nuevos Datos

```
nuevos_datos = [[5.0, 3.2, 1.5, 0.3]]
prediccion = modelo.predict(nuevos_datos)
# Resultado: 'Iris-setosa'
```

---

## 8. Aprendizaje No Supervisado

### ¿Qué es?
En el aprendizaje no supervisado, **NO hay etiquetas**. El objetivo es descubrir **patrones ocultos** en los datos.

### Analogía: Piezas de LEGO
Le das a un niño piezas de LEGO de diferentes colores y formas y le pides que las agrupe. El niño puede:
- Agrupar por color
- Agrupar por tamaño
- Agrupar por tipo

No hay una respuesta "correcta" predefinida.

---

### Clustering (Agrupamiento)

**Clustering** agrupa datos similares en **clusters** (grupos).

**Características:**
- Dentro de un cluster: datos MUY similares
- Entre clusters: datos DIFERENTES
- **Outliers:** Datos que no encajan en ningún cluster

---

### Casos de Uso de Clustering

#### 1. Segmentación de Mercado

**Input:**
- Tamaño del hogar
- Ingresos
- Ubicación
- Ocupación

**Output (Clusters):**
- "Familia pequeña"
- "Grandes gastadores"
- "Solteros jóvenes"

**Aplicación:** Campañas de marketing dirigidas.

---

#### 2. Detección de Anomalías (Outliers)

**Ejemplo: Transacciones con tarjeta de crédito**

```
Cluster Normal:
  - Compras de $10-$200
  - Frecuencia: 2-5 por semana

Outlier (Fraude potencial):
  - Compra de $5,000 ⚠️
  - 20 transacciones en 1 hora ⚠️
```

---

#### 3. Sistemas de Recomendación

**Ejemplo: Netflix**

**Datos del usuario:**
- Sesiones de visualización
- Minutos por sesión
- Shows únicos vistos

**Clustering:**
```
Cluster 1: Fans de acción
Cluster 2: Amantes de comedias
Cluster 3: Documentales
```

**Resultado:** Recomendaciones personalizadas.

---

### Medidas de Similitud

Para hacer clustering, necesitamos medir **qué tan similares** son dos objetos.

**Similitud:** Valor entre 0 y 1
- 0 = Completamente diferentes
- 1 = Idénticos

**Ejemplo: Frutas**
```
Manzana vs Cereza (por color rojo)
Similitud = 0.9 (muy similares)

Manzana vs Plátano (color diferente)
Similitud = 0.2 (poco similares)
```

**Métricas comunes:**
- Distancia Euclidiana
- Distancia Manhattan
- Similitud Coseno
- Similitud Jaccard

---

### Proceso de Clustering

```
1. Preparar datos
   ├── Eliminar valores faltantes
   ├── Normalizar
   └── Escalar features

2. Crear matriz de similitud
   └── Calcular distancias entre puntos

3. Ejecutar algoritmo de clustering
   ├── K-Means (basado en particiones)
   ├── Hierarchical (jerárquico)
   ├── DBSCAN (basado en densidad)
   └── Gaussian Mixture (basado en distribución)

4. Interpretar resultados
   └── Verificar calidad de clusters
```

---

## 9. Aprendizaje por Refuerzo

### ¿Qué es?
**Reinforcement Learning** es cuando un agente aprende a tomar decisiones mediante **prueba y error**, recibiendo recompensas o castigos.

### Analogía: Entrenar a un Perro

```
Acción: El perro recoge una pelota
   ↓
Recompensa: Le das un premio 🦴
   ↓
Aprendizaje: El perro repite la acción
```

```
Acción: El perro muerde los muebles
   ↓
Castigo: Le dices "No" 🚫
   ↓
Aprendizaje: El perro evita la acción
```

---

### Componentes Clave

| Componente | Definición | Ejemplo (Auto autónomo) |
|------------|------------|-------------------------|
| **Agent** (Agente) | Quien aprende | El auto |
| **Environment** (Ambiente) | Mundo donde opera | La carretera |
| **State** (Estado) | Situación actual | Cámara muestra el camino |
| **Action** (Acción) | Decisión que toma | Girar izquierda/derecha/recto |
| **Reward** (Recompensa) | Señal de qué tan buena fue la acción | +10 por mantenerse en el carril |
| **Policy** (Política) | Estrategia del agente | Reglas de conducción |

---

### Proceso de Reinforcement Learning

```
    ┌──────────┐
    │  Agent   │
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Environment│
    └────┬─────┘
         │
    ┌────▼─────┐
    │  State   │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Action  │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Reward  │
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Learning │
    └──────────┘
```

---

### Ejemplo: Auto Autónomo

**Ciclo de aprendizaje:**

1. **State:** Cámara frontal muestra la carretera
2. **Action:** Mantener el carril
3. **Reward:** +10 puntos ✅
4. **Learning:** "Mantener el carril es bueno"

**Otro ciclo:**

1. **State:** Cámara muestra peatón cruzando
2. **Action:** Frenar
3. **Reward:** +50 puntos ✅✅
4. **Learning:** "Frenar para peatones es MUY bueno"

**Ciclo negativo:**

1. **State:** Semáforo en rojo
2. **Action:** Acelerar
3. **Reward:** -100 puntos ❌
4. **Learning:** "Pasar semáforo en rojo es MALO"

---

### Aplicaciones de Reinforcement Learning

| Aplicación | Descripción |
|------------|-------------|
| **Autos autónomos** | Aprender a navegar tráfico |
| **Robots** | Optimizar movimientos |
| **Juegos** | AlphaGo ganó al campeón mundial de Go |
| **Recomendaciones** | Optimizar qué contenido mostrar |
| **Brazo robótico** | Colocar productos en almacén eficientemente |

---

### Ejemplo Detallado: Brazo Robótico en Almacén

**Objetivo:** Colocar productos en ubicaciones correctas.

**1. Setup del ambiente:**
- Brazo robótico
- Diseño del almacén
- Productos a colocar
- Ubicaciones objetivo

**2. State representation:**
- Posición del brazo
- Posición del producto
- Posición de las ubicaciones objetivo

**3. Action space:**
- Mover brazo arriba/abajo/izquierda/derecha
- Abrir/cerrar pinza

**4. Rewards y penalties:**
```
✅ +10: Producto colocado correctamente
❌ -5: Producto caído
❌ -2: Producto dañado
❌ -1: Fallo en colocar correctamente
```

**5. Training:**
- El brazo prueba acciones aleatorias al inicio
- Observa recompensas/castigos
- Aprende qué acciones maximizan recompensas
- Mejora su estrategia con el tiempo

**6. Resultado:**
Después de miles de iteraciones, el brazo aprende estrategias óptimas para colocar productos.

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Qué tipo de algoritmo de Machine Learning se usa para predecir el precio de reventa de una propiedad residencial?**

- ○ Clasificación Multi-clase
- ○ Clasificación Binaria
- ○ Detección de Anomalías
- ✅ Regresión

**Explicación:** Regresión predice valores numéricos continuos como precios.

---

### Pregunta 2
**¿Qué algoritmo se usa para predecir valores numéricos continuos?**

- ✅ Regresión Lineal
- ○ Clasificación con Árboles de Decisión
- ○ K-Means Clustering
- ○ Regresión Logística

**Explicación:** Regresión Lineal modela relaciones entre variables para predecir valores continuos.

---

### Pregunta 3
**¿Qué tipo de algoritmo de Machine Learning aprende de resultados para tomar decisiones?**

- ✅ Aprendizaje por Refuerzo
- ○ Procesamiento de Lenguaje Natural
- ○ Aprendizaje No Supervisado
- ○ Aprendizaje Supervisado

**Explicación:** Reinforcement Learning aprende mediante recompensas y castigos.

---

## 🎓 Consejos para el Examen

### Diferencias Clave

| Regresión | Clasificación |
|-----------|---------------|
| Salida continua (números) | Salida categórica (clases) |
| Ejemplo: Precio, temperatura | Ejemplo: Spam/No spam, categorías |
| Algoritmo: Regresión Lineal | Algoritmo: Regresión Logística |

### Tipos de ML - Resumen

| Tipo | Datos | Objetivo | Ejemplo |
|------|-------|----------|---------|
| **Supervisado** | Etiquetados | Predicción | Precio de casa |
| **No Supervisado** | Sin etiquetas | Patrones | Segmentación |
| **Por Refuerzo** | Recompensas | Decisiones óptimas | Auto autónomo |

### Términos Importantes

- **Training:** Enseñar al modelo
- **Testing:** Evaluar el modelo
- **Accuracy:** Predicciones correctas / Total
- **Loss:** Error entre predicción y realidad
- **Inference:** Usar modelo entrenado para predecir

---

## 📚 Resumen del Módulo

| Concepto | Puntos Clave |
|----------|--------------|
| **ML** | Aprender de ejemplos sin programación explícita |
| **Supervisado** | Datos etiquetados → Predicción |
| **Regresión** | Predice números (precio, temperatura) |
| **Clasificación** | Predice categorías (spam, sentimiento) |
| **No Supervisado** | Descubre patrones sin etiquetas |
| **Clustering** | Agrupa datos similares |
| **Refuerzo** | Aprende por recompensas/castigos |

---

## ✅ Checklist de Preparación

Antes de avanzar, asegúrate de poder:

- [ ] Explicar la diferencia entre regresión y clasificación
- [ ] Describir cómo funciona la regresión lineal
- [ ] Entender la función sigmoid en regresión logística
- [ ] Explicar clustering con un ejemplo
- [ ] Describir los componentes de reinforcement learning
- [ ] Identificar cuándo usar cada tipo de ML
- [ ] Calcular accuracy básico