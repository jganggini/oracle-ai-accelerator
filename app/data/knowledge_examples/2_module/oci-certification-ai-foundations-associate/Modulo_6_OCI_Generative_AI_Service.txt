# Módulo 6: Servicio de IA Generativa de OCI

## 📋 Información del Módulo

**Peso en el examen:** 15%  
**Conceptos evaluados:**
- Descripción del Servicio de IA Generativa de OCI
- Autonomous Database Select AI
- Oracle Vector Search

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Describir las características del Servicio de IA Generativa de OCI
2. Comprender los modelos foundacionales disponibles
3. Entender el proceso de fine-tuning
4. Conocer AI Vector Search en Oracle Database 23ai
5. Usar Select AI para consultas en lenguaje natural

---

## 1. OCI Generative AI Service

### Descripción General

**OCI Generative AI** es un servicio completamente gestionado que proporciona modelos de lenguaje grandes (LLM) personalizables a través de una **API única**.

**Características clave:**
- 🎯 **Serverless:** Sin infraestructura que gestionar
- 🔄 **API única:** Cambia entre modelos fácilmente
- 🔒 **Seguro:** Tus datos permanecen en tu tenancy
- ⚙️ **Personalizable:** Fine-tuning con tus datos

---

### Tres Pilares del Servicio

```
┌─────────────────────────────────────┐
│  OCI GENERATIVE AI SERVICE          │
│                                     │
│  1 MODELOS PRE-ENTRENADOS           │
│     - Cohere (Command-R, R-Plus)    │
│     - Meta (Llama 3)                │
│     - Embeddings multilingües       │
│                                     │
│  2 FINE-TUNING FLEXIBLE             │
│     - T-Few (rápido y eficiente)    │
│     - Modelos personalizados        │
│                                     │
│  3 CLUSTERS DE IA DEDICADOS         │
│     - GPUs aisladas                 │
│     - RDMA networking               │
│     - Seguridad garantizada         │
└─────────────────────────────────────┘
```

---

### ¿Cómo Funciona?

**Flujo básico:**

```
Entrada (Prompt) → OCI Gen AI Service → Respuesta
```

**Ejemplo:**
```
Prompt: "Explica qué es fotosíntesis en términos simples"

Servicio: Procesa con modelo LLM

Respuesta: "La fotosíntesis es el proceso por el cual 
            las plantas convierten luz solar, agua y 
            dióxido de carbono en glucosa (azúcar) y 
            oxígeno..."
```

---

### Casos de Uso

| Caso de Uso | Descripción |
|-------------|-------------|
| **Chat** | Asistentes conversacionales |
| **Generación de texto** | Artículos, emails, contenido |
| **Resumen** | Condensar documentos largos |
| **Extracción de información** | Sacar datos clave de texto |
| **Búsqueda semántica** | Encontrar info por significado |
| **Clasificación** | Categorizar contenido |

---

## 2. Modelos Pre-entrenados

### Modelos de Chat

#### 1. Cohere Command-R-Plus

**Características:**
- 💪 **Más potente** de la familia Cohere
- 📄 **128,000 tokens** de contexto
- 💰 **Más costoso**
- 🎯 **Casos avanzados**

**Cuándo usar:**
- ✅ Documentos muy largos
- ✅ Conversaciones complejas
- ✅ Múltiples tareas en un prompt
- ✅ Razonamiento avanzado

---

#### 2. Cohere Command-R

**Características:**
- ⚡ **Más rápido** y **económico**
- 📄 **16,000 tokens** de contexto
- 💵 **Costo-efectivo**
- 🎯 **Casos generales**

**Cuándo usar:**
- ✅ Conversaciones estándar
- ✅ Documentos medianos
- ✅ Presupuesto limitado
- ✅ Respuestas rápidas

---

#### 3. Meta Llama 3 70B Instruct

**Características:**
- 🦙 **Open source** (Meta)
- 📄 **8,000 tokens** de contexto
- 🎯 **Instruction-tuned**
- 💪 **70 mil millones de parámetros**

**Cuándo usar:**
- ✅ Preferencia por open source
- ✅ Tareas de instrucción
- ✅ Integración con ecosistema Llama

---

### Comparación de Modelos de Chat

| Modelo | Tokens Max | Costo | Mejor Para |
|--------|-----------|-------|------------|
| **Command-R-Plus** | 128K | 💰💰💰 | Casos avanzados |
| **Command-R** | 16K | 💰 | Uso general |
| **Llama 3 70B** | 8K | 💰💰 | Open source |

---

### Modelos de Chat: Características Especiales

**Contexto conversacional:**
```
Usuario: ¿Cuál es la capital de Francia?
Bot: La capital de Francia es París.

Usuario: ¿Cuál es su población?
Bot: París tiene aproximadamente 2.2 millones de habitantes 
     en la ciudad propiamente dicha, y cerca de 12 millones 
     en el área metropolitana.
```

**El bot recuerda** que "su" se refiere a París.

---

### Modelos de Embedding

#### 1. Cohere Embed English

**Características:**
- 🇬🇧 **Solo inglés**
- 🔍 **Búsqueda semántica**
- 📊 **Similitud de documentos**

**Uso:**
```
Texto: "Machine learning is amazing"
↓
Embedding: [0.23, -0.45, 0.67, ..., 0.12]
           (vector de 1024 dimensiones)
```

---

#### 2. Cohere Embed Multilingual

**Características:**
- 🌍 **100+ idiomas**
- 🔄 **Búsqueda cross-idioma**
- 🎯 **Más versátil**

**Ejemplos de uso:**

**Búsqueda dentro del mismo idioma:**
```
Query (francés): "voiture électrique"
Docs (francés): Documentos sobre autos eléctricos
```

**Búsqueda cross-idioma:**
```
Query (chino): "电动汽车"
Docs (francés): Documentos sobre autos eléctricos
```

---

### Embeddings: Aplicación Práctica

**Problema:**
Tienes 10,000 documentos de soporte técnico. Usuario pregunta: "¿Cómo resetear mi contraseña?"

**Solución con embeddings:**

```
1. Pre-procesamiento (una vez):
   Para cada documento:
   Doc → Embed Model → Vector
   Guardar en Vector Database

2. Query del usuario:
   "¿Cómo resetear mi contraseña?"
   ↓
   Embed Model → Vector query
   ↓
   Buscar vectores similares en DB
   ↓
   Top 3 documentos más relevantes
   ↓
   Enviar a LLM con contexto
   ↓
   Respuesta fundamentada
```

**Ventaja sobre búsqueda por palabras clave:**
```
Búsqueda tradicional:
Query: "resetear contraseña"
Solo encuentra: docs con palabras exactas

Búsqueda semántica:
Query: "resetear contraseña"
Encuentra: 
- "resetear contraseña" ✅
- "restaurar password" ✅
- "cambiar credenciales" ✅
- "recuperar acceso" ✅
```

---

## 3. Fine-Tuning en OCI Generative AI

### ¿Qué es Fine-Tuning?

**Definición:**
Tomar un modelo pre-entrenado y entrenarlo con **datos específicos** de tu dominio.

```
Modelo Base (Conocimiento general)
        +
Tus Datos (Conocimiento específico)
        ↓
Modelo Fine-tuned (Especializado)
```

---

### Beneficios del Fine-Tuning

#### 1. Mejor Desempeño en Tarea Específica

**Sin fine-tuning:**
```
Prompt: "Analiza este contrato legal..."
Respuesta: Términos generales, posiblemente incorrectos
```

**Con fine-tuning (dominio legal):**
```
Prompt: "Analiza este contrato legal..."
Respuesta: Análisis preciso con terminología legal correcta
```

---

#### 2. Mayor Eficiencia

**Antes (prompts largos):**
```
Prompt (1000 tokens):
"Eres un experto en atención al cliente de un banco.
Respondes en tono formal y profesional.
Conoces estos productos: [lista de productos]
Políticas: [lista de políticas]
...

Pregunta del usuario (10 tokens): 
¿Cómo abro una cuenta?"

Total: 1010 tokens
```

**Después (modelo fine-tuned):**
```
Prompt (10 tokens):
"¿Cómo abro una cuenta?"

Total: 10 tokens
```

**Ahorro:** 100x menos tokens → Más rápido y barato

---

### T-Few Fine-Tuning

**T-Few** es el método de fine-tuning de Oracle.

**Características:**
- ⚡ **Rápido:** Mucho más rápido que full fine-tuning
- 💰 **Económico:** Menos recursos computacionales
- 🎯 **Eficiente:** Solo actualiza pequeña fracción de pesos

**Cómo funciona:**

```
Modelo Pre-entrenado:
┌────────────────────────┐
│ Capa 1 (congelada) ❄️  │
│ Capa 2 (congelada) ❄️  │
│ [Nueva capa T-Few] 🔥  │ ← Solo esta capa se entrena
│ Capa 3 (congelada) ❄️  │
│ Capa 4 (congelada) ❄️  │
└────────────────────────┘
```

**Ventajas vs Full Fine-tuning:**
- ✅ 10-100x más rápido
- ✅ 10-100x más barato
- ✅ Menor riesgo de overfitting
- ✅ Menos datos necesarios

---

### Proceso de Fine-Tuning

```
1. Preparar Datos
   ├── Formato: JSON con pares (prompt, completion)
   ├── Cantidad: Miles de ejemplos
   └── Calidad: Alta, representativa

2. Crear Dedicated AI Cluster
   ├── Seleccionar GPUs
   └── Configurar para fine-tuning

3. Entrenar Modelo
   ├── Subir datos
   ├── Configurar T-Few
   ├── Iniciar entrenamiento
   └── Monitorear progreso

4. Evaluar Modelo
   ├── Test con datos de validación
   └── Comparar con modelo base

5. Desplegar
   ├── Crear endpoint
   └── Usar en producción
```

---

### Ejemplo de Datos de Fine-Tuning

**Dominio: Soporte técnico de software**

```json
{
  "data": [
    {
      "prompt": "¿Cómo actualizo el software?",
      "completion": "Para actualizar: 1) Ve a Configuración > Actualización 2) Haz clic en 'Buscar actualizaciones' 3) Si hay una disponible, haz clic en 'Instalar'. El proceso tarda 5-10 minutos."
    },
    {
      "prompt": "Error 404 al abrir documento",
      "completion": "El error 404 indica que el archivo no se encuentra. Verifica: 1) Que el archivo no se haya movido 2) Que tengas permisos 3) Intenta reabrir desde el historial reciente."
    },
    {
      "prompt": "¿Cómo exporto a PDF?",
      "completion": "Para exportar a PDF: 1) Abre el documento 2) Ve a Archivo > Exportar 3) Selecciona formato PDF 4) Elige ubicación 5) Haz clic en 'Guardar'."
    }
  ]
}
```

**Necesitas:** Miles de ejemplos similares.

---

## 4. Dedicated AI Clusters

### ¿Qué son?

**Dedicated AI Clusters** son recursos de **GPU aislados** para tus workloads de GenAI.

**Componentes:**
```
┌──────────────────────────────────┐
│  DEDICATED AI CLUSTER            │
│                                  │
│  ┌────────────────────────────┐  │
│  │   GPU Pool                 │  │
│  │   - NVIDIA A100/H100       │  │
│  │   - Aisladas por cliente   │  │
│  └────────────────────────────┘  │
│              ↕                   │
│  ┌────────────────────────────┐  │
│  │   RDMA Networking          │  │
│  │   - Ultra baja latencia    │  │
│  │   - Alto throughput        │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

---

### Tipos de Clusters

#### 1. Hosting Cluster
**Para:** Servir tráfico de inferencia

```
Modelo Fine-tuned
      ↓
Hosting Cluster
      ↓
Endpoint HTTP
      ↓
Aplicación hace requests
```

---

#### 2. Fine-tuning Cluster
**Para:** Entrenar modelos personalizados

```
Modelo Base + Datos
      ↓
Fine-tuning Cluster
      ↓
Modelo Fine-tuned
```

---

### Seguridad y Aislamiento

**Garantías:**
- 🔒 **GPUs aisladas:** Tus GPUs no comparten con otros clientes
- 🛡️ **Red dedicada:** Networking RDMA exclusivo
- 🔐 **Datos seguros:** Tus datos nunca salen de tu tenancy
- ✅ **Cumplimiento:** Cumple regulaciones de seguridad

---

## 5. Playground de OCI Gen AI

### ¿Qué es el Playground?

**Interfaz visual** para probar modelos **sin escribir código**.

**Usos:**
- 🧪 Experimentar con prompts
- 🔧 Ajustar parámetros
- 📊 Ver resultados en tiempo real
- 💻 Copiar código generado

---

### Sección Chat

**Funcionalidades:**

1. **Seleccionar modelo:**
```
Dropdown:
- Command-R-Plus
- Command-R
- Llama 3 70B
```

2. **Escribir prompt:**
```
"Explícame qué son los agujeros negros"
```

3. **Ver respuesta:**
```
"Los agujeros negros son regiones del espacio 
 donde la gravedad es tan intensa que nada, 
 ni siquiera la luz, puede escapar..."
```

4. **Ajustar configuración:**
```
- Preamble Override (cambiar comportamiento)
- Temperature (aleatoriedad)
- Top-k, Top-p (selección de tokens)
- Max tokens (largo de respuesta)
```

---

### Preamble Override

**Definición:**
Mensaje inicial que **cambia el comportamiento** del modelo.

**Ejemplo:**

**Preamble por defecto:**
```
"Eres un asistente útil y preciso."
```

**Preamble personalizado:**
```
"Eres un asesor de viajes. Responde en tono de pirata.
 Siempre recomienda aventuras emocionantes."
```

**Resultado:**
```
Usuario: "¿Dónde debo viajar?"

Respuesta: "¡Arrr! Te recomiendo las Islas del Caribe, 
           marinero. Ahí encontrarás tesoros escondidos 
           y aventuras en altamar. ¡Zarpa hacia Jamaica!"
```

---

### Parameters (Parámetros)

#### Temperature
**Controla aleatoriedad.**

```
Temperature = 0.0
→ Respuesta determinística (siempre la misma)
→ Mejor para: Tareas que requieren precisión

Temperature = 1.0
→ Respuesta creativa (varía cada vez)
→ Mejor para: Escritura creativa, brainstorming
```

**Ejemplo:**
```
Prompt: "Completa: El cielo es..."

Temperature 0.0:
"El cielo es azul."

Temperature 1.0:
"El cielo es un lienzo de posibilidades infinitas."
```

---

### Sección Embeddings

**Visualización de embeddings.**

**Ejemplo: Artículos de recursos humanos**

```
Input: 41 títulos de artículos de RH

Proceso:
1. Convertir cada título a embedding
2. Reducir dimensiones para visualización (2D)
3. Graficar en mapa 2D

Resultado:
┌───────────────────────────────┐
│  Cluster 1: Habilidades       │
│  • #24 Habilidades técnicas   │
│  • #19 Desarrollo profesional │
│  • #18 Habilidades de negocio │
│                               │
│  Cluster 2: Vacaciones        │
│  • #15 Política de vacaciones │
│  • #12 Tarjeta de tiempo      │
│  • #08 Días festivos          │
└───────────────────────────────┘
```

**Interpretación:**
- Artículos cercanos → Semánticamente similares
- Artículos lejanos → Temáticas diferentes

---

### Ver Código (View Code)

**Después de probar en Playground:**

```
1. Haz clic en "View Code"

2. Selecciona lenguaje:
   - Python
   - Java

3. Copia el código

4. Pega en tu IDE

5. ¡Funciona!
```

**Ejemplo de código Python generado:**
```python
import oci

# Configuración
config = oci.config.from_file()
client = oci.generative_ai_inference.GenerativeAiInferenceClient(config)

# Request
request = oci.generative_ai_inference.models.GenerateTextDetails(
    prompt="Explica fotosíntesis",
    model_id="cohere.command-r-plus",
    max_tokens=500,
    temperature=0.7
)

# Llamada
response = client.generate_text(request)
print(response.data.inference_response.generated_text)
```

---

## 6. Oracle AI Vector Search

### ¿Qué es Vector Search?

**Búsqueda por similitud semántica** usando embeddings en Oracle Database 23ai.

**Ventajas:**
- 🔍 Búsqueda por **significado**, no palabras exactas
- 📊 Combina datos relacionales + vectores
- ⚡ Alto rendimiento
- 🔒 Seguridad de Oracle Database

---

### Tipo de Dato VECTOR

**Nuevo tipo de dato en Oracle Database 23ai.**

**Crear tabla con vectores:**
```sql
CREATE TABLE documentos (
    id NUMBER,
    texto VARCHAR2(4000),
    embedding VECTOR(1024)  -- Vector de 1024 dimensiones
);
```

**También puedes omitir dimensiones:**
```sql
CREATE TABLE documentos (
    id NUMBER,
    texto VARCHAR2(4000),
    embedding VECTOR  -- Dimensión flexible
);
```

---

### Generar Embeddings en la Base de Datos

**Opción 1: Usar API externa**
```sql
-- Llamar a OCI Gen AI desde PL/SQL
```

**Opción 2: Cargar modelo ONNX**
```sql
-- Cargar modelo ResNet-50
EXEC DBMS_VECTOR.LOAD_ONNX_MODEL(
  'resnet_50',
  '/path/to/resnet50.onnx'
);

-- Usar modelo para generar embedding
SELECT VECTOR_EMBEDDING(
  resnet_50 USING imagen AS data
) as embedding
FROM imagenes;
```

---

### Función VECTOR_DISTANCE

**Calcula distancia entre vectores.**

```sql
SELECT 
    texto,
    VECTOR_DISTANCE(
        embedding,
        :query_vector,
        COSINE  -- Métrica de distancia
    ) as distancia
FROM documentos
ORDER BY distancia
FETCH FIRST 5 ROWS ONLY;
```

**Métricas de distancia:**
- `COSINE` (por defecto)
- `EUCLIDEAN`
- `DOT`

**Interpretación:**
- Distancia pequeña → Vectores similares → Documentos relacionados

---

### Búsqueda de Similitud con SQL

**Ejemplo: Buscar empleados con skills similares**

```sql
SELECT 
    c.nombre_candidato,
    j.titulo_puesto,
    VECTOR_DISTANCE(
        c.resume_embedding,
        j.job_embedding,
        COSINE
    ) AS similarity_score
FROM 
    candidatos c,
    puestos j
WHERE 
    j.ciudad IN ('Madrid', 'Barcelona')
ORDER BY 
    similarity_score
FETCH FIRST 10 ROWS ONLY;
```

**Resultado:**
```
Nombre         | Puesto              | Score
---------------|---------------------|-------
Ana García     | Senior Developer    | 0.05
Carlos Ruiz    | DevOps Engineer     | 0.08
María López    | Full Stack Dev      | 0.12
```

**Score bajo = Alta similitud**

---

### Vector Indexes

**Crear índices para búsquedas rápidas.**

**Sintaxis:**
```sql
CREATE VECTOR INDEX idx_resume
ON candidatos(resume_embedding)
ORGANIZATION INMEMORY NEIGHBOR GRAPH  -- Para datasets en memoria
DISTANCE COSINE
WITH TARGET ACCURACY 95;
```

**Opciones de organización:**
- `INMEMORY NEIGHBOR GRAPH`: Dataset cabe en memoria
- `NEIGHBOR PARTITIONS`: Dataset muy grande

---

### Target Accuracy

**Controla calidad vs velocidad.**

```
TARGET ACCURACY 80:
- Más rápido
- 80% de resultados correctos en top-k

TARGET ACCURACY 95:
- Más lento
- 95% de resultados correctos en top-k

TARGET ACCURACY 99:
- Más lento aún
- 99% de resultados correctos en top-k
```

---

### Búsqueda Aproximada

**Keyword: APPROXIMATE**

```sql
SELECT nombre, skills
FROM candidatos
ORDER BY VECTOR_DISTANCE(
    resume_embedding,
    :query_vector
)
FETCH APPROXIMATE FIRST 5 ROWS ONLY
WITH TARGET ACCURACY 90;
```

**Beneficios:**
- ⚡ Mucho más rápido que búsqueda exacta
- 🎯 Precisión controlable
- 📈 Escalable a millones de vectores

---

### Similitud en JOINs

**Combinar búsqueda vectorial con SQL tradicional.**

```sql
SELECT 
    a.nombre_autor,
    b.titulo_libro,
    p.contenido_pagina
FROM 
    autores a
    JOIN libros b ON a.autor_id = b.autor_id
    JOIN paginas p ON b.libro_id = p.libro_id
WHERE 
    b.genero = 'Ficción'
    AND a.pais_origen = 'India'
ORDER BY 
    VECTOR_DISTANCE(
        p.page_embedding,
        :query_embedding
    )
FETCH FIRST 5 ROWS ONLY;
```

**Ventaja:**
Combina filtros tradicionales (género, país) con similitud semántica.

---

## 7. Select AI

### ¿Qué es Select AI?

**Consulta bases de datos usando lenguaje natural.**

**Ejemplo:**
```
Usuario: "Muestra las 10 películas más vistas"

Select AI:
1. Traduce a SQL
2. Ejecuta query
3. Retorna resultados
```

---

### Cómo Funciona

```
┌───────────────────────────┐
│ Usuario hace pregunta     │
│ en lenguaje natural       │
└───────────────────────────┘
             ↓
┌───────────────────────────┐
│ Select AI                 │
│ - Conecta con LLM         │
│ - Genera SQL óptimo       │
│ - Ejecuta query           │
└───────────────────────────┘
             ↓
┌───────────────────────────┐
│ Resultados                │
│ - Tabla                   │
│ - Narrativa               │
│ - SQL (opcional)          │
└───────────────────────────┘
```

---

### Sintaxis

```sql
SELECT AI 
¿Cuáles son las 5 películas más vistas este año?;
```

**Ver SQL generado:**
```sql
SELECT AI SHOWSQL
¿Cuáles son las 5 películas más vistas este año?;
```

**Resultado:**
```sql
-- SQL Generado:
SELECT titulo, vistas
FROM peliculas
WHERE EXTRACT(YEAR FROM fecha_lanzamiento) = 2024
ORDER BY vistas DESC
FETCH FIRST 5 ROWS ONLY;
```

---

### AI Profiles

**Configurar qué LLM usar y qué tablas incluir.**

```sql
-- Crear AI Profile con OCI Gen AI
BEGIN
  DBMS_CLOUD_AI.CREATE_PROFILE(
    profile_name => 'mi_perfil_genai',
    attributes => JSON_OBJECT(
      'provider' VALUE 'oci',
      'model' VALUE 'cohere.command-r',
      'object_list' VALUE JSON_ARRAY(
        JSON_OBJECT('owner' VALUE 'HR', 'name' VALUE 'employees'),
        JSON_OBJECT('owner' VALUE 'HR', 'name' VALUE 'departments')
      )
    )
  );
END;
/
```

**Usar perfil:**
```sql
EXEC DBMS_CLOUD_AI.SET_PROFILE('mi_perfil_genai');

SELECT AI ¿Cuántos empleados hay en IT?;
```

---

### Ventajas de Select AI

| Ventaja | Descripción |
|---------|-------------|
| **Accesibilidad** | No necesitas saber SQL |
| **Velocidad** | Consultas en segundos |
| **Precisión** | LLM genera SQL optimizado |
| **Seguridad** | Datos quedan en tu tenancy |
| **Flexibilidad** | Cambia de LLM fácilmente |

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Cómo difieren los modelos de chat de los modelos de embeddings en OCI Generative AI?**

- ○ Los modelos de chat son para queries de búsqueda, los embeddings procesan imágenes
- ✅ Los modelos de chat generan texto, los embeddings convierten texto en representaciones numéricas
- ○ Ambos modelos realizan la misma función
- ○ Los embeddings generan respuestas de texto, los chats se enfocan en representaciones vectoriales

**Explicación:** Chat genera respuestas textuales, embeddings convierten texto a vectores para búsqueda.

---

### Pregunta 2
**¿Cuál es el propósito principal del Playground de OCI en Generative AI?**

- ○ Desplegar modelos de IA para producción
- ○ Almacenar embeddings para búsqueda vectorial
- ✅ Explorar visualmente y probar modelos pre-entrenados y fine-tuned sin escribir código
- ○ Gestionar recursos de GPU para entrenamiento de IA

**Explicación:** Playground permite experimentar con modelos visualmente antes de integrarlos en aplicaciones.

---

### Pregunta 3
**Tu empresa quiere hacer fine-tuning de un LLM pre-entrenado para responder mejor a queries de clientes sobre reservas de viajes. ¿Qué recurso se requiere en OCI?**

- ○ Model Catalog
- ○ Object Storage Bucket
- ○ AI Vision Service
- ✅ Dedicated AI Cluster

**Explicación:** Dedicated AI Clusters proveen recursos de GPU necesarios para fine-tuning.

---

## 🎓 Consejos para el Examen

### Modelos de OCI Gen AI

| Modelo | Contexto | Costo | Uso |
|--------|----------|-------|-----|
| **Command-R-Plus** | 128K tokens | 💰💰💰 | Avanzado |
| **Command-R** | 16K tokens | 💰 | General |
| **Llama 3 70B** | 8K tokens | 💰💰 | Open source |

### Fine-Tuning

**Cuándo usar:**
- ✅ Dominio especializado
- ✅ Estilo/tono específico
- ✅ Mejor desempeño necesario

**T-Few ventajas:**
- ⚡ Rápido
- 💰 Económico
- 🎯 Eficiente

### Vector Search

**Conceptos clave:**
- `VECTOR` datatype
- `VECTOR_DISTANCE()` función
- `APPROXIMATE` búsqueda
- `TARGET ACCURACY` precision

### Select AI

**Sintaxis básica:**
```sql
SELECT AI pregunta en lenguaje natural;
SELECT AI SHOWSQL pregunta;
```

---

## 📚 Resumen del Módulo

| Concepto | Puntos Clave |
|----------|--------------|
| **OCI Gen AI** | Servicio serverless con modelos pre-entrenados |
| **Modelos Chat** | Command-R, R-Plus, Llama 3 |
| **Embeddings** | Conversión de texto a vectores |
| **Fine-tuning** | T-Few para personalización eficiente |
| **Dedicated Clusters** | GPUs aisladas para workloads |
| **Vector Search** | Búsqueda semántica en Oracle DB |
| **Select AI** | SQL mediante lenguaje natural |

---

## ✅ Checklist de Preparación

Antes de avanzar, asegúrate de poder:

- [ ] Comparar Command-R vs R-Plus vs Llama 3
- [ ] Explicar diferencia entre chat y embeddings
- [ ] Describir T-Few fine-tuning
- [ ] Entender Dedicated AI Clusters
- [ ] Explicar tipo VECTOR en Oracle DB
- [ ] Usar VECTOR_DISTANCE()
- [ ] Describir Select AI

