# Módulo 3: Fundamentos de Deep Learning

## 📋 Información del Módulo

**Peso en el examen:** 10%  
**Conceptos evaluados:**
- Fundamentos de Deep Learning
- Modelos Convolucionales (CNN)
- Modelos de Secuencia (RNN & LSTM)

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Explicar qué es Deep Learning y cómo difiere de ML tradicional
2. Comprender las Redes Neuronales Artificiales (ANN)
3. Entender las CNN para procesamiento de imágenes
4. Conocer los modelos de secuencia (RNN y LSTM)
5. Identificar aplicaciones de cada arquitectura

---

## 1. ¿Qué es Deep Learning?

### Definición
**Deep Learning (DL)** es un subconjunto de Machine Learning que se enfoca en entrenar **redes neuronales artificiales** con muchas capas (profundas) para resolver tareas complejas.

### Característica Principal
La capacidad de **procesar datos crudos** (como píxeles de imagen) y **extraer patrones automáticamente**, sin necesidad de definir características manualmente.

---

### Ejemplo: Reconocimiento de Dígitos Escritos a Mano

**Problema:**
Cada persona escribe números de manera diferente. ¿Cómo entrenar una máquina para reconocer cualquier dígito?

```
Diferentes formas de escribir "7":
  7   ㄱ   7   ₇   7̅
```

**Solución con Deep Learning:**

```
Imagen (28×28 píxeles)
    ↓
Red Neuronal Artificial (ANN)
    ├── Detecta bordes
    ├── Detecta curvas
    └── Combina patrones
    ↓
Predicción: "7"
```

**Ventaja clave:**
No necesitas decirle a la red qué características buscar. La red **aprende automáticamente** qué patrones son importantes.

---

### Deep Learning vs Machine Learning Tradicional

| Aspecto | Machine Learning | Deep Learning |
|---------|------------------|---------------|
| **Features** | Definidas manualmente | Extraídas automáticamente |
| **Datos** | Funciona con pocos datos | Requiere MUCHOS datos |
| **Computación** | CPU suficiente | Requiere GPU |
| **Interpretabilidad** | Más fácil de explicar | "Caja negra" |
| **Aplicaciones** | Datos estructurados | Imágenes, audio, texto |

---

### Historia de Deep Learning

```
1950s: Concepto de neurona artificial
  ↓
1980s: Backpropagation (ajuste de pesos)
  ↓
1990s: CNN para análisis de imágenes
  ↓
2000s: GPU se vuelven más potentes y baratas
  ↓
2010s: GPU ampliamente disponibles
  ├── 2012: AlexNet (ImageNet)
  ├── 2016: Modelos generativos
  └── 2020+: LLMs (ChatGPT, GPT-4)
```

---

## 2. Redes Neuronales Artificiales (ANN)

### Inspiración: El Cerebro Humano

**Neurona biológica:**
```
Dendritas → Núcleo → Axón → Sinapsis
(Entrada)   (Procesa) (Salida) (Conexión)
```

**Neurona artificial:**
```
Inputs → Pesos → Suma → Activación → Output
(x₁,x₂)   (w₁,w₂)   (Σ)     (f)      (y)
```

---

### Componentes de una ANN

#### 1. Capas (Layers)

```
┌──────────────┐
│ Input Layer  │ ← Datos de entrada
└──────────────┘
       ↓
┌──────────────┐
│ Hidden Layer │ ← Procesamiento
│ Hidden Layer │
└──────────────┘
       ↓
┌──────────────┐
│ Output Layer │ ← Resultado
└──────────────┘
```

**Tipos de capas:**
- **Input Layer (Entrada):** Recibe los datos (OBLIGATORIA)
- **Hidden Layers (Ocultas):** Procesan información (OPCIONALES, múltiples)
- **Output Layer (Salida):** Produce el resultado (OBLIGATORIA)

---

#### 2. Neuronas

Cada neurona:
1. Recibe múltiples entradas
2. Las multiplica por pesos
3. Suma todo
4. Aplica función de activación
5. Produce una salida

**Ejemplo matemático:**
```
Inputs: x₁ = 2, x₂ = 3
Pesos: w₁ = 0.5, w₂ = 0.3
Bias: b = 1

Suma ponderada:
z = (x₁ × w₁) + (x₂ × w₂) + b
z = (2 × 0.5) + (3 × 0.3) + 1
z = 1 + 0.9 + 1 = 2.9

Activación (ReLU):
output = max(0, z) = 2.9
```

---

#### 3. Pesos (Weights)

Los **pesos** determinan la importancia de cada conexión.

**Analogía:**
En un examen:
- Pregunta 1 tiene peso 0.3 (30%)
- Pregunta 2 tiene peso 0.7 (70%)

Si sacas 80% en ambas:
```
Nota final = (80 × 0.3) + (80 × 0.7) = 80%
```

Pero si:
- Pregunta 1: 100%
- Pregunta 2: 60%

```
Nota final = (100 × 0.3) + (60 × 0.7) = 72%
```

Los pesos dan más importancia a ciertas entradas.

---

#### 4. Funciones de Activación

Deciden si una neurona debe "activarse" o no.

**Funciones comunes:**

| Función | Fórmula | Uso |
|---------|---------|-----|
| **ReLU** | f(x) = max(0, x) | Capas ocultas (más común) |
| **Sigmoid** | f(x) = 1/(1+e^-x) | Clasificación binaria |
| **Tanh** | f(x) = (e^x - e^-x)/(e^x + e^-x) | Datos centrados en 0 |
| **Softmax** | Normaliza probabilidades | Multi-clase |

**Gráfica ReLU:**
```
    y
    │     ╱
    │    ╱
    │   ╱
────┼───────→ x
    │
```

---

#### 5. Bias

El **bias** permite flexibilidad al modelo, similar a la "constante" en una ecuación.

**Sin bias:**
```
y = 2x
```
Solo puede pasar por el origen (0,0)

**Con bias:**
```
y = 2x + 3
```
Puede desplazarse verticalmente

---

### Ejemplo Completo: Reconocer Dígitos

**Arquitectura:**

```
Input: 28×28 = 784 píxeles
    ↓
Hidden Layer 1: 16 neuronas
    ↓
Hidden Layer 2: 16 neuronas
    ↓
Output: 10 neuronas (0-9)
```

**Proceso:**
1. Imagen de "2" entra como 784 números
2. Capas ocultas detectan patrones (curvas, bordes)
3. Capa de salida predice: neurona #2 se activa

---

### Entrenamiento: Backpropagation

**Problema:**
¿Cómo ajustamos los pesos para que la red aprenda?

**Solución: Backpropagation**

```
1. Forward Pass (Predicción)
   Imagen → Red → Predicción: "6"
   
2. Calcular Error
   Real: "2"
   Predicho: "6"
   Error = grande ❌
   
3. Backward Pass
   Ajustar pesos para reducir error
   
4. Repetir miles de veces
   Imagen → Red → Predicción: "2" ✅
```

**Analogía:**
Como practicar tiros libres en baloncesto:
1. Tiras y fallas
2. Ajustas tu técnica
3. Tiras de nuevo
4. Repites hasta acertar consistentemente

---

## 3. Modelos de Secuencia (RNN y LSTM)

### ¿Qué son Secuencias?

**Secuencias** son datos donde el **orden importa**.

**Ejemplos:**
- Texto: "El perro come" ≠ "Come el perro"
- Audio: Serie de sonidos en el tiempo
- Video: Secuencia de frames
- Series de tiempo: Precios de acciones

---

### Aplicaciones de Modelos de Secuencia

| Aplicación | Input → Output |
|------------|----------------|
| **Traducción** | Texto en inglés → Texto en francés |
| **Reconocimiento de voz** | Audio → Texto |
| **Generación de música** | Notas previas → Siguiente nota |
| **Predicción de clima** | Datos históricos → Temperatura futura |
| **Lenguaje de señas** | Secuencia de gestos → Texto |

---

### Recurrent Neural Networks (RNN)

**Característica principal:**
RNN tienen **memoria**. Cada paso depende del anterior.

**Arquitectura:**

```
Entrada:    x₁  →  x₂  →  x₃  →  x₄
             ↓      ↓      ↓      ↓
Estado:    [h₁] → [h₂] → [h₂] → [h₄]
             ↓      ↓      ↓      ↓
Salida:     y₁     y₂     y₃     y₄
```

**Flujo de información:**
- Datos fluyen de izquierda a derecha
- Cada paso comparte información con el siguiente

---

### Tipos de Arquitecturas RNN

#### 1. One-to-One
```
1 Input → 1 Output
```
**No** es realmente secuencial. Es como una red normal.

---

#### 2. One-to-Many
```
1 Input → Múltiples Outputs
```
**Ejemplo:** Generación de música
```
Input: Nota inicial "Do"
Output: Do → Re → Mi → Fa → Sol
```

---

#### 3. Many-to-One
```
Múltiples Inputs → 1 Output
```
**Ejemplo:** Análisis de sentimiento
```
Input: "La película fue excelente y emocionante"
Output: Sentimiento = Positivo
```

---

#### 4. Many-to-Many
```
Múltiples Inputs → Múltiples Outputs
```
**Ejemplo:** Traducción automática
```
Input: "How are you?"
Output: "¿Cómo estás?"
```

---

### Problema de RNN: Vanishing Gradient

**Limitación:**
RNN tienen **mala memoria a largo plazo**. Olvidan información de pasos muy anteriores.

**Ejemplo:**
```
Oración: "El gato, que vive en la casa azul de mi abuela, come pescado"

Pregunta: ¿Quién come pescado?
```

RNN puede olvidar que estamos hablando del "gato" porque hay mucho texto en el medio.

---

### Long Short-Term Memory (LSTM)

**Solución al problema de RNN:**
LSTM puede **recordar información a largo plazo** mediante "compuertas" (gates).

---

### Cómo Funciona LSTM

**Componentes principales:**

```
┌─────────────────────┐
│   LSTM Cell         │
│                     │
│ ┌─────────────────┐ │
│ │ Forget Gate     │ │ ¿Qué olvidar?
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ Input Gate      │ │ ¿Qué recordar?
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ Output Gate     │ │ ¿Qué compartir?
│ └─────────────────┘ │
└─────────────────────┘
```

---

#### 1. Forget Gate (Compuerta de Olvido)
**Decide qué información eliminar de la memoria.**

**Ejemplo:**
```
Texto: "El gato es negro. El perro es blanco."
```
Cuando llega "El perro", puede olvidar información sobre el gato.

---

#### 2. Input Gate (Compuerta de Entrada)
**Decide qué información nueva agregar a la memoria.**

**Ejemplo:**
```
"El perro es blanco"
```
Guarda: color del perro = blanco

---

#### 3. Output Gate (Compuerta de Salida)
**Decide qué información mostrar como salida.**

**Ejemplo:**
```
Pregunta: "¿Qué color es el perro?"
```
Output Gate recupera: "blanco"

---

### Proceso LSTM Paso a Paso

```
1. Input actual + Estado oculto anterior
   ↓
2. Forget Gate decide qué olvidar
   ↓
3. Input Gate decide qué recordar
   ↓
4. Actualizar Cell State (memoria)
   ↓
5. Output Gate decide qué mostrar
   ↓
6. Generar output y nuevo estado oculto
```

---

### RNN vs LSTM

| Característica | RNN | LSTM |
|----------------|-----|------|
| **Memoria** | Corto plazo | Largo plazo |
| **Complejidad** | Simple | Más complejo |
| **Velocidad** | Más rápido | Más lento |
| **Vanishing Gradient** | Sí ❌ | No ✅ |
| **Aplicaciones** | Secuencias cortas | Secuencias largas |

---

## 4. Convolutional Neural Networks (CNN)

### ¿Para Qué se Usan las CNN?

**CNN** son especializadas en procesar **imágenes** y **videos**.

**Ventaja principal:**
Detectan automáticamente patrones visuales como:
- Bordes
- Texturas
- Formas
- Objetos

---

### Problema con Redes Neuronales Normales para Imágenes

**Imagen de 28×28 píxeles:**
```
Red normal:
- Convierte imagen a vector 1D: 784 números
- Pierde información espacial
- No aprovecha que píxeles cercanos están relacionados
```

**CNN:**
```
- Procesa imagen en 2D
- Mantiene relaciones espaciales
- Detecta patrones locales
```

---

### Arquitectura CNN

```
Input Image
    ↓
Convolutional Layers
    ↓
Pooling Layers
    ↓
Flatten
    ↓
Fully Connected Layers
    ↓
Output (Clasificación)
```

---

### Componentes de CNN

#### 1. Convolutional Layer (Capa Convolucional)

**Función:**
Detecta características mediante **filtros** (kernels).

**Ejemplo: Detector de bordes verticales**

```
Filtro 3×3:
[-1  0  1]
[-1  0  1]
[-1  0  1]
```

Este filtro desliza sobre la imagen detectando bordes verticales.

**Proceso:**
```
Imagen original:
[10 10 10 | 50 50 50]
[10 10 10 | 50 50 50]
[10 10 10 | 50 50 50]

Aplicar filtro:
[0  0  | 40 40]
[0  0  | 40 40]
```

¡El filtro detectó el borde vertical! ✅

---

#### 2. Activation Function (ReLU)

Después de convolución, se aplica **ReLU** para no linealidad.

```
ReLU(x) = max(0, x)
```

**Efecto:**
- Valores positivos → Mantener
- Valores negativos → 0

---

#### 3. Pooling Layer (Capa de Agrupamiento)

**Función:**
**Reducir dimensiones** manteniendo información importante.

**Max Pooling 2×2:**
```
Entrada:
[2  8  | 3  1]
[5  1  | 7  2]
──────────────
[4  6  | 9  3]
[0  2  | 1  5]

Max Pooling:
[8  7]
[6  9]
```

**Ventajas:**
- ⬇️ Reduce tamaño
- 🚀 Menos computación
- 🛡️ Reduce overfitting

---

#### 4. Flatten

**Convierte matriz 2D → vector 1D**

```
Entrada (2×2):
[8  7]
[6  9]

Flatten:
[8, 7, 6, 9]
```

---

#### 5. Fully Connected Layers

**Red neuronal normal** que hace la clasificación final.

```
[8, 7, 6, 9] →  Dense Layer → Output: "Gato"
```

---

### Analogía: Robot Inspector de Casas

**Herramienta 1: Detector de planos (Convolutional Layer)**
- Escanea partes de la casa
- Busca patrones específicos

**Herramienta 2: Marcador de patrones (Activation)**
- Resalta áreas detectadas

**Herramienta 3: Resumidor (Pooling)**
- Captura características más importantes de cada habitación

**Herramienta 4: Experto en casas (Fully Connected)**
- Analiza todos los patrones
- Decide qué tipo de casa es

**Herramienta 5: Adivinador (Softmax)**
- Asigna probabilidades a tipos de casa

**Herramienta 6: Control de calidad (Dropout)**
- Evita confiar demasiado en un solo patrón

---

### Aplicaciones de CNN

| Aplicación | Descripción |
|------------|-------------|
| **Clasificación de imágenes** | ¿Es un gato o un perro? |
| **Detección de objetos** | Dónde están los objetos (bounding boxes) |
| **Segmentación** | Etiquetar cada píxel (cielo, árbol, calle) |
| **Reconocimiento facial** | Identificar personas |
| **Imágenes médicas** | Detección de tumores |
| **Autos autónomos** | Reconocer señales de tránsito, peatones |
| **Análisis satelital** | Clasificación de uso de tierra |

---

### Limitaciones de CNN

| Limitación | Descripción |
|------------|-------------|
| **Computacionalmente costosas** | Requieren GPU potentes |
| **Necesitan muchos datos** | Miles de imágenes etiquetadas |
| **Overfitting** | Si hay pocos datos |
| **Caja negra** | Difícil interpretar decisiones |
| **Sensibles a cambios** | Pequeños cambios pueden causar errores |

---

## 5. Arquitecturas de Deep Learning - Resumen

| Arquitectura | Datos | Aplicación |
|--------------|-------|------------|
| **FNN** (Feedforward) | Tabulares | Predicción de precios |
| **CNN** | Imágenes, videos | Clasificación de imágenes |
| **RNN** | Secuencias | Predicción de series de tiempo |
| **LSTM** | Secuencias largas | Traducción, análisis de sentimiento |
| **Autoencoders** | Cualquier tipo | Compresión, anomalías |
| **GAN** | Imágenes | Generación de imágenes realistas |
| **Transformers** | Texto | ChatGPT, traducción |

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Qué modelo de secuencia puede mantener información relevante en secuencias largas?**

- ○ Redes Neuronales Recurrentes
- ✅ Redes Neuronales de Memoria a Corto y Largo Plazo (LSTM)
- ○ Redes Neuronales Feedforward
- ○ Redes Neuronales Convolucionales

**Explicación:** LSTM está diseñado específicamente para manejar dependencias a largo plazo, resolviendo el problema del vanishing gradient.

---

### Pregunta 2
**¿Qué red neuronal tiene un bucle de retroalimentación y está diseñada para manejar datos secuenciales?**

- ○ Redes Neuronales Feedforward
- ✅ Redes Neuronales Recurrentes
- ○ Redes Neuronales Convolucionales
- ○ Redes Neuronales de Perceptrón Multicapa

**Explicación:** RNN tienen conexiones de retroalimentación que permiten procesar secuencias.

---

### Pregunta 3
**¿Qué componente esencial de una Red Neuronal Artificial realiza suma ponderada y aplica función de activación?**

- ○ Iterador
- ○ Bias
- ✅ Neurona
- ○ Clasificador

**Explicación:** La neurona es la unidad fundamental que procesa información.

---

## 🎓 Consejos para el Examen

### Diferencias Clave

| Modelo | Datos | Memoria | Aplicación |
|--------|-------|---------|------------|
| **CNN** | Imágenes | No | Clasificación de imágenes |
| **RNN** | Secuencias | Corto plazo | Series de tiempo cortas |
| **LSTM** | Secuencias | Largo plazo | Traducción, NLP |

### Arquitecturas - Resumen Rápido

**Pregunta del examen: ¿Qué modelo usar para...?**

- 📸 Imágenes → **CNN**
- 🎵 Música/Texto → **RNN o LSTM**
- 📈 Predicción numérica → **FNN**
- 🎨 Generar imágenes → **GAN**

### Componentes de ANN

| Componente | Función |
|------------|---------|
| **Capas** | Organizan neuronas (input, hidden, output) |
| **Neuronas** | Unidades de procesamiento |
| **Pesos** | Importancia de conexiones |
| **Activation** | Decide si neurona se activa |
| **Bias** | Flexibilidad del modelo |

---

## 📚 Resumen del Módulo

| Concepto | Puntos Clave |
|----------|--------------|
| **Deep Learning** | Redes neuronales profundas, múltiples capas |
| **ANN** | Neuronas conectadas en capas |
| **Backpropagation** | Ajuste de pesos para aprender |
| **CNN** | Especializada en imágenes, usa filtros |
| **RNN** | Memoria a corto plazo, datos secuenciales |
| **LSTM** | Memoria a largo plazo, compuertas |

---

## ✅ Checklist de Preparación

Antes de avanzar, asegúrate de poder:

- [ ] Explicar la diferencia entre ML y DL
- [ ] Describir los componentes de una ANN
- [ ] Entender cómo funciona backpropagation
- [ ] Identificar cuándo usar CNN vs RNN
- [ ] Explicar el problema del vanishing gradient
- [ ] Describir las compuertas de LSTM
- [ ] Dar ejemplos de aplicaciones de cada arquitectura

