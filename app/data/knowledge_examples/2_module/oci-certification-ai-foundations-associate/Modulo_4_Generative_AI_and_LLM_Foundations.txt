# Módulo 4: IA Generativa y Fundamentos de Modelos de Lenguaje Grande (LLM)

## 📋 Información del Módulo

**Peso en el examen:** 15%  
**Conceptos evaluados:**
- Descripción general de IA Generativa
- Fundamentos de Modelos de Lenguaje Grande (LLM)
- Fundamentos de Transformers
- Prompt Engineering e Instruction Tuning
- Fine-tuning de LLMs

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Explicar qué es la IA Generativa y cómo funciona
2. Comprender los Modelos de Lenguaje Grande (LLM)
3. Entender la arquitectura Transformer
4. Dominar conceptos de Prompt Engineering
5. Conocer métodos de fine-tuning y personalización de LLMs

---

## 1. Introducción a la IA Generativa

### ¿Qué es IA Generativa?

**Definición:**
La **IA Generativa (GenAI)** es un tipo de inteligencia artificial que puede **crear contenido nuevo** como texto, imágenes, música, videos y otros tipos de datos.

### Analogía Simple

**Machine Learning tradicional:**
```
Entrada: Imagen de un perro
Salida: Etiqueta "perro"
```

**IA Generativa:**
```
Entrada: Descripción "Un perro jugando en el parque"
Salida: Imagen NUEVA de un perro jugando en el parque
```

---

### ¿Cómo Funciona la IA Generativa?

```
1. Entrenamiento
   ├── Modelo ve miles de imágenes de perros
   ├── Aprende patrones: orejas, cola, pelaje
   └── No copia imágenes, aprende conceptos
   
2. Generación
   ├── Usuario pide: "perro jugando"
   ├── Modelo usa patrones aprendidos
   └── Crea imagen NUEVA basada en conceptos
```

**Punto clave:** El modelo NO está copiando. Está **generando** basándose en patrones aprendidos.

---

### IA Generativa vs Machine Learning

| Aspecto | Machine Learning | IA Generativa |
|---------|------------------|---------------|
| **Objetivo** | Clasificar / Predecir | Crear contenido nuevo |
| **Entrada** | Datos + Etiquetas | Datos sin etiquetas (pre-training) |
| **Salida** | Etiqueta / Número | Texto / Imagen / Audio |
| **Ejemplo** | "Esta es una foto de gato" | "Crea una imagen de un gato" |
| **Proceso** | Aprende relación datos→etiqueta | Aprende patrones en contenido |

---

### Tipos de Modelos Generativos

#### 1. Basados en Texto
**Generan contenido textual:**
- Historias y poemas
- Código de programación
- Artículos
- Diálogos y chat

**Ejemplos:**
- ChatGPT
- GPT-4
- Claude
- Llama

---

#### 2. Multimodales
**Procesan y generan múltiples tipos de contenido:**
- Texto ↔ Imagen
- Texto ↔ Audio
- Texto ↔ Video

**Ejemplos:**
- DALL-E (Texto → Imagen)
- Midjourney (Texto → Imagen)
- Stable Diffusion (Texto → Imagen)
- Whisper (Audio → Texto)

---

### Aplicaciones de IA Generativa

| Vertical | Aplicación |
|----------|------------|
| **Creación de contenido** | Artículos, blogs, marketing |
| **Arte y diseño** | Imágenes, logos, diseños |
| **Programación** | Generación de código, debugging |
| **Medicina** | Diseño de medicamentos, análisis de imágenes |
| **Educación** | Tutores personalizados, contenido educativo |
| **Entretenimiento** | Guiones, música, videojuegos |

---

## 2. Modelos de Lenguaje Grande (LLM)

### ¿Qué es un Modelo de Lenguaje?

**Definición:**
Un **modelo de lenguaje** es un modelo probabilístico que determina la probabilidad de una secuencia de palabras.

### Analogía: Completar la Oración

```
Oración: "Fui al zoológico y me enviaron un _____"

Probabilidades:
- león: 0.03
- elefante: 0.02
- perro: 0.45
- gato: 0.25
- pantera: 0.15
```

El modelo calcula probabilidades para **cada palabra en su vocabulario**.

---

### Cómo Funciona la Predicción

**Paso 1: Calcular probabilidades**
```
Entrada: "Fui al zoológico y me enviaron un"
↓
Modelo LLM
↓
Probabilidades para cada palabra
```

**Paso 2: Seleccionar la palabra con mayor probabilidad**
```
Palabra seleccionada: "perro" (0.45)
```

**Paso 3: Agregar a la entrada y repetir**
```
Nueva entrada: "Fui al zoológico y me enviaron un perro"
↓
Modelo LLM
↓
Probabilidades:
- EOS (End of Sentence): 0.85 ← ALTA
- gato: 0.05
- y: 0.10
```

**Paso 4: Terminar cuando aparece EOS**
```
Salida final: "Fui al zoológico y me enviaron un perro"
```

---

### ¿Qué es "Large" (Grande) en LLM?

**"Large" se refiere al número de parámetros.**

**Parámetros:** Pesos ajustables en la red neuronal.

**Evolución del tamaño:**

| Año | Modelo | Parámetros |
|-----|--------|------------|
| 2018 | GPT-1 | 117 millones |
| 2019 | GPT-2 | 1.5 mil millones |
| 2020 | GPT-3 | 175 mil millones |
| 2023 | GPT-4 | >1 trillón (no confirmado) |

**Nota importante:**
Más parámetros ≠ Siempre mejor desempeño

Puede causar **overfitting** si el modelo es demasiado grande.

---

### Capacidades de LLMs

#### 1. Responder Preguntas
```
Usuario: ¿Cuál es la capital de Francia?
LLM: La capital de Francia es París.
```

#### 2. Razonamiento Complejo
```
Usuario: Tengo 3 manzanas. Compro 2 bolsas con 5 manzanas cada una. 
        Le doy 4 a mi amigo. ¿Cuántas me quedan?

LLM: Empiezas con 3 manzanas.
     Compras 2 bolsas × 5 = 10 manzanas más.
     Total: 3 + 10 = 13 manzanas.
     Das 4 a tu amigo.
     Te quedan: 13 - 4 = 9 manzanas.
```

#### 3. Generar Artículos
```
Usuario: Escribe un artículo sobre la Revolución Francesa

LLM: La Revolución Francesa fue un período de cambio radical...
     [Genera artículo completo]
```

#### 4. Traducir Idiomas
```
Usuario: Traduce "How are you" al francés

LLM: "Comment allez-vous" (formal) o "Comment ça va" (informal)
```

---

## 3. Arquitectura Transformer

### ¿Por Qué Transformers?

**Problema con RNN:**
```
Oración: "Jane lanzó el frisbee y su perro lo recogió"

RNN procesa así:
Paso 1: Jane
Paso 2: Jane → lanzó
Paso 3: Jane → lanzó → el
...

Problema: Procesa SECUENCIALMENTE (lento)
         Olvida información lejana
```

---

### Solución: Transformers

**Transformers pueden ver TODA la oración al mismo tiempo.**

```
Oración: "Jane lanzó el frisbee y su perro lo recogió"

Transformer ve:
Jane ←→ lanzó ←→ frisbee ←→ perro ←→ recogió
  ↕       ↕         ↕         ↕        ↕
Todas las conexiones simultáneamente
```

**Ventajas:**
- ✅ Ve toda la oración a la vez
- ✅ Paralelización (más rápido)
- ✅ Captura relaciones a largo plazo
- ✅ Entiende contexto completo

---

### Mecanismo de Auto-Atención (Self-Attention)

**Self-Attention** le permite al modelo **enfocarse** en partes importantes de la entrada.

**Ejemplo:**
```
Oración: "Jane lanzó el frisbee y su perro lo recogió"

Pregunta: ¿A qué se refiere "lo"?
```

**Self-Attention:**
```
"lo" presta atención a:
- frisbee (ALTA atención) ✅
- perro (Media atención)
- Jane (Baja atención)
- lanzó (Baja atención)

Conclusión: "lo" = frisbee
```

---

### Componentes del Transformer

```
┌─────────────────────────┐
│     TRANSFORMER         │
│                         │
│  ┌──────────────────┐   │
│  │    ENCODER       │   │
│  │  - Procesa input │   │
│  │  - Crea          │   │
│  │    embeddings    │   │
│  └──────────────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │    DECODER       │   │
│  │  - Genera output │   │
│  │  - Usa           │   │
│  │    embeddings    │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

---

### Encoder (Codificador)

**Función:**
Procesa el **texto de entrada** y lo convierte en **representaciones numéricas** (embeddings).

**Proceso:**
```
Texto: "El gato come pescado"
   ↓
Tokenización: ["El", "gato", "come", "pescado"]
   ↓
Encoder
   ↓
Embeddings: [0.2, 0.5, ...], [0.8, 0.1, ...], ...
```

**Aplicaciones de Encoder-only:**
- Búsqueda semántica
- Bases de datos vectoriales
- Clasificación de texto

---

### Decoder (Decodificador)

**Función:**
Genera **texto de salida** palabra por palabra.

**Proceso:**
```
Embeddings de entrada
   ↓
Decoder
   ↓
Token 1: "El"
   ↓
Decoder (con "El" como input)
   ↓
Token 2: "gato"
   ↓
...continúa hasta EOS
```

**Aplicaciones de Decoder-only:**
- Generación de texto
- ChatGPT
- Completar código

---

### Encoder-Decoder (Combinado)

**Función:**
Combina ambos para tareas de **secuencia a secuencia**.

**Ejemplo: Traducción**
```
Entrada (Inglés): "How are you?"
   ↓
Encoder → Embeddings
   ↓
Decoder → Salida (Francés): "Comment allez-vous?"
```

**Aplicaciones:**
- Traducción automática
- Resumen de texto
- Conversión de formatos

---

## 4. Tokens y Tokenización

### ¿Qué es un Token?

**Token:** Unidad básica que entiende un LLM.

**Un token puede ser:**
- Una palabra completa: "apple"
- Parte de una palabra: "friend" + "ship"
- Símbolo de puntuación: "." o ","

---

### Ejemplos de Tokenización

**Texto simple:**
```
"I love AI"
Tokens: ["I", "love", "AI"]
Total: 3 tokens
```

**Texto complejo:**
```
"Machine learning is indivisible."

Tokens: ["Machine", "learning", "is", "in", "divisible", "."]
Total: 6 tokens
```

---

### Reglas Generales

| Tipo de Texto | Tokens por Palabra |
|---------------|-------------------|
| **Simple** | ~1 token/palabra |
| **Complejo** | ~2-3 tokens/palabra |

**Ejemplo práctico:**
```
"Many words map to one token, but indivisible words require multiple."

Tokens:
Many(1) words(1) map(1) to(1) one(1) token(1), (1) 
but(1) in(1)divisible(1) words(1) require(1) multiple(1).(1)

Total: 15 tokens
```

---

## 5. Embeddings

### ¿Qué son Embeddings?

**Definición:**
**Embeddings** son representaciones numéricas de texto que capturan su significado.

### Analogía: Mapa de Conceptos

Imagina un mapa donde:
- Palabras similares están **cerca**
- Palabras diferentes están **lejos**

```
        Gato
         │
    ┌────┼────┐
  Perro Mascota Felino
    │         │
  Animal    Tigre
```

---

### Proceso de Embedding

```
Texto: "El perro come"
   ↓
Tokenización: ["El", "perro", "come"]
   ↓
Encoder Model
   ↓
Embeddings (vectores):
El    → [0.1, 0.5, 0.3, 0.8, ...]
perro → [0.2, 0.7, 0.1, 0.5, ...]
come  → [0.9, 0.2, 0.6, 0.3, ...]
```

**Cada token → Vector de números**

---

### Aplicación: Búsqueda Semántica

**Problema tradicional (búsqueda por palabras clave):**
```
Búsqueda: "auto"
Resultados: Solo documentos con palabra "auto"
No encuentra: "coche", "vehículo", "automóvil"
```

**Solución con embeddings (búsqueda semántica):**
```
1. Convertir todos los documentos a embeddings
2. Guardar en base de datos vectorial
3. Convertir consulta del usuario a embedding
4. Encontrar documentos con embeddings similares
5. Retornar resultados relevantes
```

**Ventaja:**
```
Búsqueda: "auto"
Resultados: 
- Documentos con "auto" ✅
- Documentos con "coche" ✅
- Documentos con "vehículo" ✅
```

---

### RAG (Retrieval-Augmented Generation)

**Problema:**
LLMs solo conocen información de su entrenamiento.

**Solución: RAG**

```
┌────────────────────────────────┐
│ 1. Usuario hace pregunta       │
└────────────────────────────────┘
              ↓
┌────────────────────────────────┐
│ 2. Buscar docs relevantes      │
│    en base vectorial           │
└────────────────────────────────┘
              ↓
┌────────────────────────────────┐
│ 3. Enviar pregunta + docs      │
│    al LLM                      │
└────────────────────────────────┘
              ↓
┌────────────────────────────────┐
│ 4. LLM genera respuesta        │
│    basada en docs              │
└────────────────────────────────┘
```

**Ejemplo:**
```
Empresa: Política de devoluciones actualizada hoy

Sin RAG:
Usuario: ¿Cuál es la política de devoluciones?
LLM: No tengo información actualizada.

Con RAG:
Usuario: ¿Cuál es la política de devoluciones?
Sistema: [Busca en docs] → Encuentra política nueva
LLM: Según la política, puedes devolver en 30-90 días...
```

---

## 6. Prompt Engineering

### ¿Qué es un Prompt?

**Prompt:** Texto de entrada que le das a un LLM.

**Prompt Engineering:** Proceso de diseñar prompts efectivos para obtener mejores resultados.

---

### Evolución: Completion → Instruction

**Modelos de Completion (antiguos):**
```
Prompt: "Four score and seven years ago"
Salida: [Completa el discurso de Gettysburg]
```

**Problema:** Solo completa texto, no sigue instrucciones.

---

**Modelos Instruction-Tuned (modernos):**
```
Prompt: "Explícame qué es fotosíntesis en términos simples"
Salida: "La fotosíntesis es el proceso por el cual las plantas 
         convierten luz solar en energía..."
```

**Ventaja:** Sigue instrucciones del usuario.

---

### Instruction Tuning

**Proceso:**
```
1. Modelo base entrenado en 2 trillones de tokens
   ↓
2. Fine-tuning con ~28,000 pares prompt-respuesta
   ↓
3. RLHF (Reinforcement Learning from Human Feedback)
   ├── Humanos escriben prompts
   ├── Humanos evalúan respuestas del modelo
   ├── Se entrena modelo de recompensa
   └── Modelo aprende preferencias humanas
   ↓
4. Modelo instruction-tuned listo
```

---

### Técnicas de Prompt Engineering

#### 1. In-Context Learning

**Definición:**
Proporcionar **ejemplos** de la tarea dentro del prompt.

**0-shot (sin ejemplos):**
```
Prompt: "Traduce al francés: cheese"
```

**Few-shot (con ejemplos):**
```
Prompt:
Traduce del inglés al francés:

Ejemplo 1:
English: hello
French: bonjour

Ejemplo 2:
English: goodbye
French: au revoir

Ejemplo 3:
English: thank you
French: merci

Ahora traduce:
English: cheese
French:
```

**Resultado:** El modelo aprende el patrón y responde mejor.

---

#### 2. Chain-of-Thought Prompting

**Definición:**
Pedir al modelo que **muestre su razonamiento** paso a paso.

**Sin Chain-of-Thought:**
```
Prompt: "Roger tiene 5 pelotas. Compra 2 latas con 3 pelotas cada una. 
         ¿Cuántas tiene?"
         
Respuesta: 11 (sin explicación)
```

**Con Chain-of-Thought:**
```
Prompt: "Roger tiene 5 pelotas. Compra 2 latas con 3 pelotas cada una. 
         ¿Cuántas tiene? Explica paso a paso."
         
Respuesta: 
Paso 1: Roger empieza con 5 pelotas
Paso 2: 2 latas × 3 pelotas = 6 pelotas nuevas
Paso 3: 5 + 6 = 11 pelotas
Respuesta final: 11 pelotas
```

**Ventaja:** Respuestas más precisas y verificables.

---

### Hallucination (Alucinación)

**Definición:**
Cuando el LLM genera texto que es **factualmente incorrecto** o **no está fundamentado** en datos.

**Ejemplo:**
```
Prompt: ¿Cuándo empezaron a manejar por la izquierda en EE.UU.?

LLM (incorrecto): "En Estados Unidos, las personas gradualmente 
                   adoptaron la práctica de manejar por el lado 
                   izquierdo del camino..."

Realidad: En EE.UU. se maneja por la DERECHA.
```

---

### Reducir Hallucination

| Método | Descripción |
|--------|-------------|
| **RAG** | Fundamentar respuestas en documentos reales |
| **Few-shot** | Proporcionar ejemplos correctos |
| **Chain-of-Thought** | Pedir razonamiento paso a paso |
| **Verificación** | Siempre verificar información crítica |

**Nota:** Actualmente NO existe un método 100% efectivo para eliminar alucinaciones.

---

## 7. Fine-Tuning de LLMs

### ¿Qué es Fine-Tuning?

**Definición:**
Tomar un modelo **pre-entrenado** y entrenarlo adicionalmente con **datos específicos** de tu dominio.

```
Modelo Pre-entrenado
(conocimiento general)
        ↓
    + Datos personalizados
    (conocimiento específico)
        ↓
  Modelo Fine-tuned
(conocimiento general + específico)
```

---

### ¿Cuándo Usar Fine-Tuning?

**Usa fine-tuning cuando:**
- ✅ El modelo no funciona bien en tu tarea
- ✅ Necesitas enseñarle algo nuevo
- ✅ Quieres un estilo/tono específico
- ✅ Dominio muy especializado (legal, médico)

**No uses fine-tuning si:**
- ❌ Prompt engineering es suficiente
- ❌ No tienes datos etiquetados
- ❌ Los datos cambian frecuentemente

---

### Proceso de Fine-Tuning

```
1. Preparar datos
   ├── Formato: pares (input, output)
   └── Cantidad: Miles de ejemplos
   
2. Entrenar modelo
   ├── Actualizar pesos
   └── T-Few (eficiente) o Full fine-tuning
   
3. Evaluar
   └── Probar en datos de test
   
4. Implementar
   └── Usar modelo personalizado
```

---

### Ejemplo de Datos para Fine-Tuning

**Dominio: Atención al cliente de un banco**

```json
[
  {
    "input": "¿Cómo abro una cuenta?",
    "output": "Para abrir una cuenta, necesitas: 1) Identificación oficial, 2) Comprobante de domicilio, 3) Visitar una sucursal o hacerlo en línea en nuestro portal."
  },
  {
    "input": "Olvidé mi contraseña",
    "output": "Puedes restablecer tu contraseña en la app: 1) Toca 'Olvidé contraseña', 2) Ingresa tu email, 3) Sigue las instrucciones del correo."
  }
]
```

**Necesitas:** Miles de ejemplos similares.

---

### Beneficios del Fine-Tuning

#### 1. Mejor Desempeño
```
Modelo base en dominio legal:
❌ Respuestas genéricas
❌ Términos incorrectos

Modelo fine-tuned:
✅ Respuestas específicas
✅ Terminología legal correcta
```

#### 2. Mayor Eficiencia
```
Antes (prompt largo):
"Eres un experto legal. Conoces derecho mexicano. 
 Respondes formalmente. [1000 tokens de contexto]
 
 Pregunta del usuario: [10 tokens]"

Después (modelo fine-tuned):
"Pregunta del usuario: [10 tokens]"

Ahorro: 1000 tokens → Más rápido y barato
```

---

## 8. Personalizar LLMs: Framework Completo

### Tres Métodos Principales

```
┌──────────────────────────────┐
│  Eje Vertical (LLM)          │
│  Optimización del LLM        │
│         ↑                    │
│         │  Fine-tuning       │
│         │                    │
│         │                    │
│  ───────┼─────────────────→  │
│         │                    │
│    Prompt    RAG             │
│  Engineering                 │
│                              │
│  Eje Horizontal (Contexto)   │
│  Más información específica  │
└──────────────────────────────┘
```

---

### 1. Prompt Engineering

**Cuándo:**
- ✅ Inicio rápido
- ✅ Sin costos de entrenamiento
- ✅ LLM ya entiende el dominio

**Ejemplo:**
```
Usuario: "Actúa como un tutor de matemáticas. 
          Explica paso a paso cómo resolver ecuaciones..."
```

---

### 2. RAG (Retrieval-Augmented Generation)

**Cuándo:**
- ✅ Datos cambian frecuentemente
- ✅ Necesitas fundamentar respuestas
- ✅ Reducir alucinaciones

**Ventajas:**
- ✅ Acceso a información actualizada
- ✅ Respuestas fundamentadas

**Desventajas:**
- ❌ Requiere base de datos compatible
- ❌ Más complejo de configurar

---

### 3. Fine-Tuning

**Cuándo:**
- ✅ LLM no funciona bien en tu tarea
- ✅ Datos demasiado grandes para prompt
- ✅ Necesitas estilo/tono específico

**Ventajas:**
- ✅ Mejor desempeño
- ✅ Modelo más eficiente

**Desventajas:**
- ❌ Requiere datos etiquetados
- ❌ Más recursos
- ❌ Tiempo de entrenamiento

---

### Estrategia Combinada

**Ruta típica:**

```
Paso 1: Empezar con Prompt Engineering
  ├── Evaluar baseline
  └── Probar few-shot

Paso 2: ¿Mejoró?
  ├── Sí → Listo ✅
  └── No → Siguiente paso

Paso 3: Agregar RAG
  ├── Conectar a knowledge base
  └── ¿Mejoró?
      ├── Sí → Listo ✅
      └── No → Siguiente paso

Paso 4: Fine-tuning
  ├── Entrenar modelo personalizado
  └── ¿Mejoró?
      ├── Sí → Posiblemente combinar con RAG
      └── No → Iterar
```

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Qué enunciado describe con precisión la IA generativa?**

- ✅ Crea contenido nuevo sin hacer predicciones
- ○ Entrena exclusivamente para predecir patrones de datos futuros
- ○ Limita funciones a generar solo salidas basadas en texto
- ○ Se enfoca en hacer predicciones precisas basadas en datos de entrenamiento

**Explicación:** IA Generativa crea contenido nuevo, no solo predice.

---

### Pregunta 2
**El fine-tuning es innecesario para LLMs si tu aplicación NO involucra cuál aspecto específico?**

- ○ Mitigación de sesgo
- ○ Vocabulario del dominio
- ○ Eficiencia y utilización de recursos
- ✅ Adaptación específica a tareas

**Explicación:** Fine-tuning se realiza principalmente para adaptación a tareas específicas.

---

### Pregunta 3
**¿Qué aspecto de los LLMs impacta significativamente sus capacidades, desempeño y requisitos de recursos?**

- ✅ Tamaño del modelo y parámetros, incluyendo número de tokens y pesos
- ○ Complejidad de los lenguajes de programación usados
- ○ Número total de GPUs usadas para entrenamiento
- ○ Número de iteraciones durante el entrenamiento

**Explicación:** El tamaño y número de parámetros tienen impacto profundo en capacidades y desempeño.

---

## 🎓 Consejos para el Examen

### Diferencias Clave

| Concepto | Descripción | Ejemplo |
|----------|-------------|---------|
| **GenAI** | Crea contenido nuevo | DALL-E genera imágenes |
| **ML** | Clasifica/Predice | Filtro de spam |
| **LLM** | Modelo de lenguaje grande | ChatGPT |

### Arquitecturas Transformer

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| **Encoder-only** | Embeddings, búsqueda | BERT |
| **Decoder-only** | Generación de texto | GPT-4 |
| **Encoder-Decoder** | Traducción | T5 |

### Personalización de LLMs

| Método | Cuándo | Ventaja |
|--------|--------|---------|
| **Prompt** | Inicio rápido | Gratis, fácil |
| **RAG** | Datos cambian | Actualizado |
| **Fine-tuning** | Dominio específico | Mejor desempeño |

---

## 📚 Resumen del Módulo

| Concepto | Puntos Clave |
|----------|--------------|
| **GenAI** | Crea contenido nuevo basándose en patrones |
| **LLM** | Modelo probabilístico de texto |
| **Transformer** | Arquitectura con self-attention |
| **Tokens** | Unidades básicas de procesamiento |
| **Embeddings** | Representación numérica de texto |
| **Prompt Engineering** | Diseño de inputs efectivos |
| **Fine-tuning** | Personalización de modelos |
| **RAG** | Fundamentar respuestas en documentos |

---

## ✅ Checklist de Preparación

Antes de avanzar, asegúrate de poder:

- [ ] Explicar la diferencia entre GenAI y ML tradicional
- [ ] Describir cómo funciona un LLM
- [ ] Entender la arquitectura Transformer
- [ ] Explicar self-attention
- [ ] Definir tokens y embeddings
- [ ] Aplicar técnicas de prompt engineering
- [ ] Describir cuándo usar fine-tuning
- [ ] Explicar cómo funciona RAG