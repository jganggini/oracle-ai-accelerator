# Módulo 1: Fundamentos de Inteligencia Artificial (AI Foundations)

## 📋 Información del Módulo

**Peso en el examen:** 10%  
**Conceptos evaluados:**
- Conceptos básicos de IA
- Aplicaciones de IA y tipos de datos
- Diferencias entre AI vs ML vs DL

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Explicar qué es la Inteligencia Artificial y sus conceptos básicos
2. Describir dominios comunes de IA y tareas relacionadas
3. Distinguir entre Inteligencia Artificial, Machine Learning y Deep Learning
4. Identificar tipos de datos utilizados en diferentes tareas de IA

---

## 1. ¿Qué es la Inteligencia Artificial?

### Definición Simple
La **Inteligencia Artificial (IA)** es la capacidad de las máquinas para imitar las habilidades cognitivas y de resolución de problemas de la inteligencia humana.

### Analogía para Entender
Piensa en la IA como enseñar a una computadora a pensar como un humano. Así como tú puedes:
- Reconocer una cara
- Entender un idioma
- Tomar decisiones
- Aprender de la experiencia

Una máquina con IA puede hacer tareas similares.

### Inteligencia Artificial General (AGI)
La **AGI** es cuando una máquina puede replicar TODAS las capacidades humanas:
- **Aprender** nuevas habilidades mediante observación
- **Pensar** de manera abstracta y razonar
- **Comunicarse** usando lenguaje
- **Crear** arte, música o ideas originales
- **Planificar** a corto y largo plazo

Cuando aplicamos AGI para resolver problemas específicos y objetivos concretos, lo llamamos **Inteligencia Artificial (IA)**.

---

## 2. Ejemplos de IA en la Vida Cotidiana

La IA está en todas partes, aunque no te des cuenta:

| Aplicación | Descripción |
|------------|-------------|
| **Clasificación de imágenes** | Identificar si una imagen es de una manzana o una naranja |
| **Filtro de spam** | Clasificar emails como spam o no spam |
| **Generación de código** | Escribir código de programación automáticamente |
| **Predicción de precios** | Estimar el precio de un auto usado |

---

## 3. Dominios y Tareas de IA

### 3.1 Lenguaje (Language)

**Tareas relacionadas con texto:**

#### a) Tareas de Texto
- Detección de idioma
- Extracción de entidades (nombres, lugares, fechas)
- Extracción de frases clave
- Traducción de texto

**Ejemplo:**
```
Entrada: "Oracle tiene su sede en Austin, Texas"
Salida: 
- Entidad: "Oracle" (Organización)
- Entidad: "Austin, Texas" (Ubicación)
```

#### b) Tareas Generativas
- Crear historias o poemas
- Resumir texto
- Responder preguntas
- Chatbots (como ChatGPT)

**Cómo funciona el texto:**
1. **Tokenización**: Convertir palabras a números
2. **Padding**: Hacer todas las oraciones del mismo largo
3. **Embeddings**: Representar palabras similares cerca unas de otras

**Modelos utilizados:**
- RNN (Redes Neuronales Recurrentes)
- LSTM (Long Short-Term Memory)
- Transformers

---

### 3.2 Audio y Voz (Speech)

**Tareas relacionadas con audio:**

#### a) Tareas de Audio
- Conversión de voz a texto (Speech-to-text)
- Reconocimiento de hablante
- Conversión de voz

#### b) Tareas Generativas
- Composición de música
- Síntesis de voz (Text-to-speech)

**Cómo funciona el audio:**
- El audio se digitaliza tomando **muestras** en el tiempo
- **Sample rate**: 44.1 kHz significa 44,100 muestras por segundo
- **Bit depth**: Cantidad de información en cada muestra

**Modelos utilizados:**
- RNN, LSTM, Transformers
- Variational Autoencoders
- Waveform models

---

### 3.3 Visión (Vision)

**Tareas relacionadas con imágenes:**

#### a) Tareas de Imagen
- Clasificar imágenes (¿es un gato o un perro?)
- Identificar objetos en una imagen
- Reconocimiento facial
- Análisis de imágenes médicas

#### b) Tareas Generativas
- Crear imágenes desde descripciones de texto
- Generar imágenes de alta resolución
- Crear modelos 3D

**Cómo funcionan las imágenes:**
- Las imágenes consisten en **píxeles**
- Los píxeles pueden ser en escala de grises o en color
- No podemos identificar una imagen mirando solo un píxel

**Modelos utilizados:**
- CNN (Redes Neuronales Convolucionales)
- YOLO (You Only Look Once)
- GANs (Redes Generativas Antagónicas)

---

### 3.4 Otras Tareas de IA

| Tarea | Descripción | Tipo de Datos |
|-------|-------------|---------------|
| **Detección de anomalías** | Detectar fraudes, fallas de máquinas | Series de tiempo |
| **Recomendaciones** | Recomendar productos | Datos de usuarios/productos similares |
| **Pronósticos** | Predecir clima, precios de acciones | Series de tiempo |

---

## 4. Diferencias entre AI, ML y DL

### 4.1 Inteligencia Artificial (AI)
**Definición:** Capacidad de las máquinas para realizar tareas que normalmente requieren inteligencia humana.

**Ejemplo:** Un auto autónomo que toma decisiones como un conductor humano (detectar peatones, cambiar de carril).

---

### 4.2 Machine Learning (ML)
**Definición:** Subconjunto de IA que se enfoca en desarrollar algoritmos que permiten a las máquinas aprender de los datos y hacer predicciones.

**Ejemplo:** Un filtro de spam que aprende a identificar correos no deseados basándose en el contenido de los emails.

**¿Qué es un algoritmo?**
Un conjunto de reglas y ecuaciones matemáticas que el modelo sigue para aprender de los datos.

---

### 4.3 Deep Learning (DL)
**Definición:** Subcampo de ML que usa redes neuronales profundas para aprender patrones complejos en los datos.

**Ejemplo:** Software de reconocimiento de imágenes que puede identificar gatos en fotos de internet.

---

### Comparación Visual

```
┌─────────────────────────────────────┐
│   Inteligencia Artificial (AI)      │
│   ┌─────────────────────────────┐   │
│   │   Machine Learning (ML)     │   │
│   │   ┌─────────────────────┐   │   │
│   │   │  Deep Learning (DL) │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 5. Tipos de Machine Learning

### 5.1 Aprendizaje Supervisado (Supervised Learning)
El algoritmo aprende de **datos etiquetados**.

**Ejemplo práctico:**
Una compañía de tarjetas de crédito quiere aprobar solicitudes automáticamente.

**Proceso tradicional:**
1. Enviar documentos ✉️
2. Verificación manual 👤
3. Revisión de puntaje crediticio 📊
4. Esperar 10-15 días ⏰

**Con Machine Learning:**
- Se usa el historial de aprobaciones pasadas
- El modelo aprende patrones
- Puede predecir si aprobar o no una nueva solicitud

**Ventajas:**
- ⚡ Más rápido
- 🤖 Automático
- 📈 Consistente

---

### 5.2 Aprendizaje No Supervisado (Unsupervised Learning)
Los datos **NO tienen etiquetas**. El objetivo es descubrir patrones o tendencias.

**Ejemplo 1: Segmentación de mercado**
Una tienda minorista analiza:
- Tamaño del hogar
- Ingresos
- Ubicación
- Ocupación

**Resultado:** Identifica grupos como "familia pequeña" o "grandes gastadores".

**Ejemplo 2: Servicios de streaming**
Netflix analiza:
- Sesiones de visualización
- Minutos por sesión
- Número de shows únicos vistos

**Resultado:** Recomienda contenido personalizado.

---

### 5.3 Aprendizaje por Refuerzo (Reinforcement Learning)
El programa aprende mediante **prueba y error**, recibiendo recompensas o castigos.

**Analogía: Aprender a jugar ajedrez**
1. 🎯 Hacer un movimiento (decisión)
2. ✅ Verificar si fue correcto (feedback)
3. 🧠 Recordar el resultado para la próxima vez (aprendizaje)

**Aplicaciones:**
- Conducción autónoma de autos
- Robots
- Juegos

---

## 6. Deep Learning Explicado

### ¿Qué es Deep Learning?
Deep Learning se especializa en **extraer características y reglas de los datos** automáticamente.

**Pregunta clave:**
¿Puedes identificar si una imagen es de un gato o un perro mirando solo un píxel?  
**No.** Necesitas ver la imagen completa.

### Redes Neuronales Artificiales (ANN)
Las ANN son como **capas de neuronas conectadas** que aprenden patrones.

**Componentes:**
1. **Capas:**
   - Capa de entrada (input)
   - Capas ocultas (hidden)
   - Capa de salida (output)

2. **Neuronas:** Unidades computacionales que procesan información

3. **Pesos:** Determinan la fuerza de conexión entre neuronas

4. **Funciones de activación:** Deciden si una neurona debe "activarse"

5. **Bias:** Flexibilidad adicional para el modelo

---

## 7. IA Generativa

**Definición:** Tipo de IA que puede **crear contenido nuevo**.

**Diferencia clave con ML tradicional:**

| Machine Learning | IA Generativa |
|------------------|---------------|
| Aprende relación datos → etiqueta | Aprende patrones en contenido |
| Salida: Clasificación/Predicción | Salida: Generación de contenido |
| Requiere datos etiquetados | No requiere etiquetas (pre-entrenamiento) |

**Ejemplos:**
- ChatGPT genera texto
- DALL-E crea imágenes desde texto
- Generación de música

---

## 8. IA Responsable y Confiable

### Tres Principios Fundamentales

Para que la IA sea confiable, debe ser:

1. **Legal (Lawful)** ⚖️
   - Cumplir con todas las leyes y regulaciones aplicables
   
2. **Ética (Ethical)** 🤝
   - Adherirse a principios éticos y valores humanos
   
3. **Robusta (Robust)** 🛡️
   - Técnicamente confiable y socialmente responsable

### Guías Éticas

La IA debe:
- ✅ Ayudar a los humanos y permitir supervisión humana
- ❌ Nunca causar daño físico o social
- 🔍 Ser transparente, justa y explicable
- 👥 Respetar la privacidad y los derechos ciudadanos

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Cuál tarea es una tarea de IA Generativa?**

- ○ Detectar fraude con tarjetas de crédito
- ○ Identificar el tema principal de un artículo de noticias
- ○ Calcular el conteo total de palabras en un artículo
- ✅ Escribir un poema basado en un tema dado

**Explicación:** Escribir un poema es una tarea de IA Generativa porque crea contenido nuevo basado en un tema o prompt.

---

### Pregunta 2
**¿Qué tipo de algoritmos de Machine Learning extrae tendencias de los datos?**

- ○ Aprendizaje Supervisado
- ✅ Aprendizaje No Supervisado
- ○ Aprendizaje por Refuerzo
- ○ Procesamiento de Lenguaje Natural

**Explicación:** El aprendizaje no supervisado extrae tendencias y patrones de datos sin etiquetas.

---

### Pregunta 3
**¿Cuál tarea es un ejemplo de una tarea relacionada con voz?**

- ✅ Conversión de voz a texto
- ○ Traducción de idiomas
- ○ Generación de números aleatorios
- ○ Composición de música

**Explicación:** La conversión de voz a texto (ASR - Automatic Speech Recognition) es una tarea específica de procesamiento de voz.

---

## 🎓 Consejos para el Examen

1. **Comprende las diferencias:** AI → ML → DL (cada uno es un subconjunto del anterior)

2. **Memoriza los dominios:**
   - Language → Texto, chatbots, traducción
   - Vision → Imágenes, objetos, reconocimiento facial
   - Speech → Audio, voz a texto

3. **Tipos de ML:**
   - Supervisado → Tiene etiquetas
   - No supervisado → Sin etiquetas, busca patrones
   - Por refuerzo → Aprende por recompensas/castigos

4. **IA Generativa:**
   - Crea contenido NUEVO
   - No solo clasifica o predice
   - Ejemplos: ChatGPT, DALL-E

5. **IA Responsable:** Legal + Ética + Robusta

---

## 📚 Resumen del Módulo

| Concepto | Definición Clave |
|----------|------------------|
| **IA** | Máquinas que imitan inteligencia humana |
| **ML** | Algoritmos que aprenden de datos |
| **DL** | Redes neuronales profundas para patrones complejos |
| **Supervisado** | Aprende con datos etiquetados |
| **No Supervisado** | Encuentra patrones sin etiquetas |
| **Por Refuerzo** | Aprende por prueba y error |
| **IA Generativa** | Crea contenido nuevo |

---

## ✅ Checklist de Preparación

Antes de avanzar al siguiente módulo, asegúrate de poder:

- [ ] Explicar qué es IA con tus propias palabras
- [ ] Dar ejemplos de IA en la vida diaria
- [ ] Distinguir entre AI, ML y DL
- [ ] Identificar los 3 dominios principales (OCI Language, OCI Vision, OCI Speech)
- [ ] Explicar los 3 tipos de Machine Learning
- [ ] Describir qué es IA Generativa
- [ ] Enumerar los 3 principios de IA Responsable

