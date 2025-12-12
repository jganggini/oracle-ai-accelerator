# Módulo 7: Servicios de IA de OCI (Profundización)

## 📋 Información del Módulo

**Peso en el examen:** 20%  
**Conceptos evaluados:**
- Exploración de servicios de IA de OCI y APIs relacionadas:
  - Language
  - Vision
  - Document Understanding
  - Speech

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Dominar las capacidades de OCI Language
2. Comprender OCI Vision y Document Understanding
3. Conocer OCI Speech en detalle
4. Identificar casos de uso apropiados para cada servicio
5. Entender cómo usar las APIs de cada servicio

---

## 1. OCI Language

### Descripción General

**OCI Language** permite análisis sofisticado de texto a escala sin experiencia en data science.

**Capacidades principales:**
1. 🌐 **Detección de idioma** (75 idiomas)
2. 😊 **Análisis de sentimiento**
3. 📝 **Extracción de frases clave**
4. 🏷️ **Clasificación de texto**
5. 👤 **Reconocimiento de entidades nombradas (NER)**
6. 🔒 **Detección de información personal (PII)**
7. 🌍 **Traducción de texto**

---

### 1.1 Detección de Idioma

**Identifica el idioma del texto.**

**Entrada:**
```
"Bonjour, comment allez-vous?"
```

**Salida:**
```json
{
  "language": "French",
  "confidence": 0.999
}
```

**Soporte:**
- 75 idiomas (de Afrikaans a Welsh)
- Confianza entre 0-1

---

### 1.2 Análisis de Sentimiento

**Tres niveles de análisis:**

#### A) Document-Level Sentiment
**Sentimiento general del texto completo.**

```
Texto: "La comida estuvo excelente, pero el servicio fue terrible."

Sentimiento del documento: MIXED
```

---

#### B) Aspect-Based Sentiment
**Sentimiento por aspectos específicos.**

```
Texto: "La comida estuvo excelente, pero el servicio fue terrible."

Aspectos detectados:
├─ comida: POSITIVE (score: 0.95)
└─ servicio: NEGATIVE (score: 0.89)
```

**Ventaja:**
Entiendes qué aspectos específicos gustan o disgustan.

---

#### C) Sentence-Level Sentiment
**Sentimiento de cada oración.**

```
Texto: "La comida fue increíble. El servicio fue lento. 
        El ambiente es agradable."

Sentimientos:
├─ Oración 1: POSITIVE
├─ Oración 2: NEGATIVE
└─ Oración 3: POSITIVE
```

---

### 1.3 Extracción de Entidades Nombradas (NER)

**Identifica 14 tipos de entidades:**

| Tipo | Ejemplos |
|------|----------|
| **PERSON** | Juan Pérez, María García |
| **LOCATION** | Madrid, España, Calle Principal |
| **ORGANIZATION** | Oracle, Microsoft, ONU |
| **DATE** | 15 de enero, 2024 |
| **TIME** | 10:30 AM, medianoche |
| **MONEY** | $100, €50, 1000 pesos |
| **QUANTITY** | 5 kg, 10 metros |
| **PERCENT** | 25%, cincuenta por ciento |
| **EMAIL** | usuario@ejemplo.com |
| **URL** | https://oracle.com |
| **PHONE** | +52-555-1234 |
| **PRODUCT** | iPhone, Oracle Database |
| **EVENT** | Olimpiadas, Conferencia Tech |
| **IP_ADDRESS** | 192.168.1.1 |

---

**Ejemplo:**

```
Texto: "Oracle abrió una oficina en Austin, Texas el 15 de marzo. 
        El CEO ganó $500,000 en bonos."

Entidades:
├─ "Oracle" → ORGANIZATION (0.99)
├─ "Austin, Texas" → LOCATION (0.95)
├─ "15 de marzo" → DATE (0.98)
├─ "CEO" → PERSON (0.85)
└─ "$500,000" → MONEY (0.99)
```

---

### 1.4 Extracción de Frases Clave

**Identifica ideas o sujetos importantes.**

```
Texto: "Las computadoras tempranas evolucionaron desde 
        simples instrumentos manuales de cálculo. 
        La comida y los servicios han mejorado."

Frases clave extraídas:
├─ "computadoras tempranas"
├─ "simples instrumentos manuales"
├─ "cálculo"
├─ "comida"
└─ "servicios"
```

---

### 1.5 Clasificación de Texto

**Clasifica en 600+ categorías organizadas jerárquicamente.**

```
Texto: "Las computadoras están revolucionando 
        la forma en que trabajamos."

Clasificación:
├─ Categoría principal: Science and Technology
└─ Subcategoría: Computer Science
```

**Jerarquía de ejemplo:**
```
Science and Technology
├── Computer Science
│   ├── Artificial Intelligence
│   ├── Databases
│   └── Software Engineering
├── Physics
└── Biology
```

---

### 1.6 Detección de Información Personal (PII)

**Identifica datos sensibles que podrían identificar a una persona.**

```
Texto: "Mi nombre es Juan Pérez, mi email es juan@email.com 
        y nací el 15/03/1990. Mi número es 555-1234."

PII detectado:
├─ "Juan Pérez" → PERSON
├─ "juan@email.com" → EMAIL
├─ "15/03/1990" → DATE
└─ "555-1234" → PHONE
```

**Uso:**
- Cumplimiento de GDPR/CCPA
- Anonimización de datos
- Auditorías de seguridad

---

### 1.7 Traducción de Texto

**Traducción neuronal entre múltiples idiomas.**

```
Entrada:
Idioma origen: Inglés
Texto: "How are you?"
Idioma destino: Francés

Salida:
"Comment allez-vous?"
```

**Características:**
- Traducción de alta calidad
- Múltiples pares de idiomas
- Contexto preservado

---

### 1.8 Modelos Personalizados

**Puedes entrenar modelos custom para:**

#### NER Personalizado
```
Dominio: Médico

Entidades custom:
├─ MEDICATION
├─ DISEASE
├─ SYMPTOM
└─ TREATMENT
```

#### Clasificación Personalizada
```
Dominio: Soporte técnico

Categorías custom:
├─ Software Issue
├─ Hardware Issue
├─ Account Problem
└─ Billing Question
```

---

## 2. OCI Vision

### Descripción General

**OCI Vision** analiza imágenes usando modelos de deep learning.

**Capacidades:**
1. 📸 **Clasificación de imágenes**
2. 🎯 **Detección de objetos**
3. 📝 **OCR (Reconocimiento de texto)**
4. 🏗️ **Modelos personalizados**

---

### 2.1 Clasificación de Imágenes

**Asigna etiquetas (tags) a imágenes completas.**

```
Entrada: [Imagen de una calle con autos]

Salida (etiquetas):
├─ "street" (0.95)
├─ "car" (0.92)
├─ "building" (0.88)
├─ "traffic" (0.85)
└─ "urban" (0.80)
```

**Score:** Confianza de 0-1 (1 = 100% seguro)

---

### 2.2 Detección de Objetos

**Encuentra objetos específicos y dibuja bounding boxes.**

```
Entrada: [Imagen de tráfico]

Salida:
┌─────────────────────────────────┐
│  [Car] 0.95                     │
│    ┌─────┐                      │
│    │     │  [Person] 0.89       │
│    └─────┘    ●                 │
│                                 │
│  [Bus] 0.92                     │
│    ┌──────────┐                 │
│    │          │                 │
│    └──────────┘                 │
└─────────────────────────────────┘

Objetos detectados:
├─ Car (x:100, y:50, w:80, h:60) - 0.95
├─ Person (x:200, y:100, w:30, h:50) - 0.89
└─ Bus (x:50, y:150, w:150, h:100) - 0.92
```

**Bounding Box:** Coordenadas (x, y, ancho, alto)

---

### 2.3 OCR (Reconocimiento de Texto)

**Extrae texto de imágenes.**

**Escenarios:**
- Letreros en fotos
- Placas de vehículos
- Documentos escaneados
- Textos en escenas

```
Entrada: [Foto de un bus con número 45]

Texto detectado:
├─ "45" (x:120, y:80)
├─ "City Transit" (x:100, y:150)
└─ "M32HOD" (placa) (x:110, y:200)
```

**Características:**
- ✅ Textos inclinados
- ✅ Diferentes fuentes
- ✅ Múltiples idiomas
- ✅ Textos pequeños

---

### 2.4 Modelos Personalizados

**Entrena modelos para objetos específicos.**

#### Detección de Objetos Custom
```
Ejemplo: Detector de antenas de microondas

Entrenar con:
├─ 500 imágenes con antenas
└─ Anotaciones (bounding boxes)

Resultado:
Modelo detecta antenas en imágenes nuevas
```

#### Clasificación Custom
```
Ejemplo: Tipos de plantas

Entrenar con:
├─ Rosa: 200 imágenes
├─ Tulipán: 200 imágenes
└─ Girasol: 200 imágenes

Resultado:
Modelo clasifica plantas en imágenes nuevas
```

---

## 3. OCI Document Understanding

### Descripción General

**Análisis avanzado de documentos** (PDFs, JPEGs, PNGs, TIFFs).

**Capacidades:**
1. 📄 **Text Recognition (OCR)**
2. 🔑 **Key-Value Extraction**
3. 📊 **Table Extraction**
4. 📋 **Document Classification**
5. 🌐 **Language Detection**

---

### 3.1 Text Recognition (OCR)

**Extrae TODO el texto del documento.**

```
Entrada: [Recibo escaneado]

Salida:
┌────────────────────────┐
│ EXAMPLE CAFÉ           │
│ 123 Main Street        │
│ ──────────────────     │
│ Americano      $4.50   │
│ Water          $1.00   │
│ ──────────────────     │
│ Total          $5.50   │
│ Date: 01/15/2024       │
└────────────────────────┘

Texto extraído (formato JSON):
{
  "lines": [
    "EXAMPLE CAFÉ",
    "123 Main Street",
    "Americano $4.50",
    ...
  ]
}
```

**Ventajas:**
- ✅ Documentos inclinados
- ✅ Texto a mano
- ✅ Mala calidad de escaneo
- ✅ Rotados

---

### 3.2 Key-Value Extraction

**Extrae pares clave-valor de tipos específicos de documentos.**

**Soporta:**
- ✅ Recibos (Receipts)
- ✅ Facturas (Invoices)  
- ✅ Pasaportes
- ✅ Licencias de conducir

**13 campos comunes:**

```
Recibo:
├─ merchant_name: "Example Café"
├─ merchant_address: "123 Main Street"
├─ merchant_phone: "555-1234"
├─ transaction_date: "2024-01-15"
├─ transaction_time: "10:30 AM"
├─ subtotal: "$5.00"
├─ tax: "$0.50"
├─ total: "$5.50"
├─ payment_method: "CREDIT CARD"
└─ items: [
      {"item": "Americano", "price": "$4.50"},
      {"item": "Water", "price": "$1.00"}
    ]
```

---

### 3.3 Table Extraction

**Extrae tablas manteniendo estructura (filas y columnas).**

```
Documento:
┌────────────┬────────┬──────────┐
│ Producto   │ Cant.  │ Precio   │
├────────────┼────────┼──────────┤
│ Laptop     │ 2      │ $1,200   │
│ Mouse      │ 5      │ $25      │
│ Teclado    │ 3      │ $75      │
└────────────┴────────┴──────────┘

JSON extraído:
{
  "tables": [
    {
      "rows": [
        {"producto": "Laptop", "cantidad": "2", "precio": "$1,200"},
        {"producto": "Mouse", "cantidad": "5", "precio": "$25"},
        {"producto": "Teclado", "cantidad": "3", "precio": "$75"}
      ]
    }
  ]
}
```

---

### 3.4 Document Classification

**Clasifica documentos en 10 tipos:**

```
Tipos soportados:
1. Invoice (Factura)
2. Receipt (Recibo)
3. Resume (CV)
4. Tax Form (Formulario fiscal)
5. Bank Statement (Estado de cuenta)
6. Legal Document (Documento legal)
7. Insurance Document (Seguro)
8. Medical Record (Registro médico)
9. Passport (Pasaporte)
10. Other (Otro)
```

**Uso:**
```
Entrada: [PDF escaneado]

Salida:
{
  "document_type": "Receipt",
  "confidence": 0.98
}
```

**Aplicación:**
Procesar documentos basándose en su tipo automáticamente.

---

### 3.5 Language Detection

**Detecta idioma basándose en características visuales del texto.**

```
Entrada: [Documento en japonés]

Salida:
{
  "language": "Japanese",
  "confidence": 0.95
}
```

**Ventaja:**
No depende del contenido textual, usa features visuales.

---

## 4. OCI Speech

### Descripción General

**Conversión de audio/video a texto** de alta precisión.

**Características:**
- 🎙️ Transcripción precisa
- ⚡ Ultra rápido (horas en <10 min)
- 🌐 Multiidioma
- 📝 Puntuación automática
- 📊 Scores de confianza
- 📺 Formato SRT para subtítulos

---

### 4.1 Idiomas Soportados

**Actualmente:**
- 🇬🇧 **English** (Inglés)
- 🇪🇸 **Spanish** (Español)
- 🇧🇷 **Portuguese** (Portugués)

**Más idiomas próximamente.**

---

### 4.2 Procesamiento Batch

**Múltiples archivos con una llamada.**

```
Input:
├─ archivo1.mp3
├─ archivo2.wav
├─ archivo3.mp4
└─ archivo4.flac

API Call:
POST /transcription-jobs
{
  "bucket": "mi-bucket",
  "files": ["archivo1.mp3", "archivo2.wav", ...]
}

Output:
├─ archivo1_transcript.json
├─ archivo2_transcript.json
├─ archivo3_transcript.json
└─ archivo4_transcript.json
```

---

### 4.3 Procesamiento Ultra Rápido

**Chunking paralelo:**

```
Audio de 2 horas
      ↓
┌─────────────────────────────┐
│ Dividir en chunks de 30 seg │
└─────────────────────────────┘
      ↓
┌───┬───┬───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │...│240│   │
└───┴───┴───┴───┴───┴───┴───┘
      ↓
┌─────────────────────────────┐
│ Procesar todos en paralelo  │
└─────────────────────────────┘
      ↓
┌─────────────────────────────┐
│ Unir transcripciones        │
└─────────────────────────────┘
      ↓
Transcripción completa en ~5 min
```

---

### 4.4 Scores de Confianza

**Dos niveles:**

#### Por Palabra
```
Transcripción: "Tengo un problema con mis auriculares"

Scores:
├─ "Tengo" (0.98)
├─ "un" (0.95)
├─ "problema" (0.99)
├─ "con" (0.97)
├─ "mis" (0.96)
└─ "auriculares" (0.92)
```

#### Por Transcripción
```
Transcripción completa:
Confidence: 0.96
```

---

### 4.5 Puntuación Automática

**Añade puntuación para mayor legibilidad.**

```
Sin puntuación:
"hola cómo estás espero que bien nos vemos mañana"

Con puntuación:
"Hola, ¿cómo estás? Espero que bien. Nos vemos mañana."
```

---

### 4.6 Normalización

**Convierte texto a formato estándar.**

**Ejemplos:**

| Literal | Normalizado |
|---------|-------------|
| "calle uno dos tres" | "Calle 123" |
| "veinticinco dólares" | "$25" |
| "www punto oracle punto com" | "www.oracle.com" |
| "quince por ciento" | "15%" |

**Tipos normalizados:**
- Direcciones
- Fechas y horas
- Números
- URLs
- Cantidades monetarias
- Porcentajes

---

### 4.7 Filtrado de Obscenidades

**Tres modos:**

#### 1. Removing
```
Original: "This is f***ing amazing!"
Resultado: "This is ******* amazing!"
```

#### 2. Masking
```
Original: "This is f***ing amazing!"
Resultado: "This is f***ing amazing!"
```

#### 3. Tagging
```
Original: "This is f***ing amazing!"
Resultado: "This is <profanity>f***ing</profanity> amazing!"
```

---

### 4.8 Formato SRT (Subtítulos)

**Genera archivos SRT para videos.**

```
1
00:00:00,000 --> 00:00:03,500
Hola, bienvenidos al tutorial.

2
00:00:03,500 --> 00:00:07,200
Hoy aprenderemos sobre inteligencia artificial.

3
00:00:07,200 --> 00:00:11,000
Empecemos con los conceptos básicos.
```

**Uso:**
- Subtítulos en YouTube
- Accesibilidad
- Videos educativos
- Cumplimiento normativo

---

### 4.9 Uso Típico

```
1. Subir audio a Object Storage
   archivo.mp3 → bucket: "transcripciones"

2. Crear trabajo de transcripción
   POST /transcription-jobs
   {
     "compartment_id": "...",
     "input_location": {
       "bucket": "transcripciones",
       "object": "archivo.mp3"
     },
     "output_location": {
       "bucket": "resultados"
     }
   }

3. Esperar (segundos a minutos)
   Estado: ACCEPTED → IN_PROGRESS → SUCCEEDED

4. Descargar resultados
   - archivo_transcript.json
   - archivo_transcript.srt (opcional)
```

---

## 5. Casos de Uso por Servicio

### OCI Language

| Caso de Uso | Servicio |
|-------------|----------|
| Clasificar tickets de soporte | Clasificación de texto |
| Moderar comentarios | Análisis de sentimiento + PII |
| Extraer datos de emails | NER |
| Traducir documentación | Traducción |
| Analizar reseñas de productos | Sentimiento por aspecto |

---

### OCI Vision

| Caso de Uso | Servicio |
|-------------|----------|
| Control de calidad en manufactura | Detección de objetos custom |
| Organizar fotos | Clasificación de imágenes |
| Leer placas de autos | OCR |
| Detectar productos en estantes | Detección de objetos |
| Moderación de contenido | Clasificación + Objetos |

---

### OCI Document Understanding

| Caso de Uso | Servicio |
|-------------|----------|
| Procesar facturas automáticamente | Key-value extraction |
| Digitalizar documentos antiguos | OCR |
| Extraer datos de formularios | Table extraction |
| Enrutamiento automático de docs | Document classification |
| Análisis de contratos | OCR + Table extraction |

---

### OCI Speech

| Caso de Uso | Servicio |
|-------------|----------|
| Transcribir llamadas de soporte | Transcripción + Normalización |
| Generar subtítulos para videos | Formato SRT |
| Análisis de meetings | Transcripción + Speech |
| Cumplimiento normativo | Transcripción con timestamps |
| Búsqueda en podcasts | Transcripción → Búsqueda texto |

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Qué servicio de IA de OCI se usa para extraer contenido tabular de documentos?**

- ○ Object Storage
- ✅ Vision
- ○ Speech
- ○ Language

**Explicación:** Document Understanding (parte de Vision) extrae tablas de documentos.

---

### Pregunta 2
**¿Qué capacidad de OCI Vision usa bounding box dentro de una imagen?**

- ○ Object Repair
- ○ Image Classification
- ○ Image Recognition
- ✅ Object Detection

**Explicación:** Object Detection localiza objetos usando bounding boxes con coordenadas.

---

### Pregunta 3
**¿Qué capacidad ofrece OCI Language Service?**

- ○ Conversión de voz a texto
- ○ Detección de objetos
- ○ Reconocimiento de imágenes
- ✅ Análisis de sentimiento de texto

**Explicación:** OCI Language analiza sentimiento a nivel de documento, aspecto y oración.

---

## 🎓 Consejos para el Examen

### Comparación de Servicios

| Servicio | Input | Output | Ejemplo |
|----------|-------|--------|---------|
| **Language** | Texto | Análisis | Sentimiento, NER |
| **Vision** | Imagen | Etiquetas/Boxes | Objetos, OCR |
| **Document** | Doc PDF/Imagen | Datos estructurados | Tablas, K-V |
| **Speech** | Audio/Video | Texto | Transcripción |

---

### Language - Capacidades Clave

| Capacidad | Función |
|-----------|---------|
| **Idioma** | Detecta 1 de 75 idiomas |
| **Sentimiento** | 3 niveles (doc, aspecto, oración) |
| **NER** | 14 tipos de entidades |
| **Frases clave** | Ideas principales |
| **Clasificación** | 600+ categorías |
| **PII** | Detecta datos sensibles |
| **Traducción** | Múltiples idiomas |

---

### Vision - Tipos de Análisis

| Tipo | Salida | Uso |
|------|--------|-----|
| **Clasificación** | Tags con scores | Categorizar imágenes |
| **Detección** | Bounding boxes | Localizar objetos |
| **OCR** | Texto extraído | Leer texto en imágenes |

---

### Document Understanding - Features

| Feature | Función |
|---------|---------|
| **OCR** | Extrae todo el texto |
| **K-V** | Pares clave-valor (recibos) |
| **Tables** | Estructura tabular |
| **Classification** | Tipo de documento (10 tipos) |

---

### Speech - Características

| Feature | Beneficio |
|---------|-----------|
| **Batch** | Múltiples archivos |
| **Rápido** | Horas en minutos |
| **Puntuación** | Legibilidad |
| **Normalización** | Formato estándar |
| **Filtrado** | Control de obscenidades |
| **SRT** | Subtítulos |
| **Confianza** | Por palabra y total |

---

## 📚 Resumen del Módulo

| Servicio | Puntos Clave |
|----------|--------------|
| **Language** | 7 capacidades, NER con 14 tipos, sentimiento 3 niveles |
| **Vision** | Clasificación, detección, OCR, modelos custom |
| **Document** | OCR, K-V extraction, tablas, 10 tipos de docs |
| **Speech** | Inglés/Español/Portugués, SRT, normalización |

---

## ✅ Checklist de Preparación

Antes del examen, asegúrate de poder:

- [ ] Listar las 7 capacidades de OCI Language
- [ ] Distinguir entre clasificación y detección en OCI Vision
- [ ] Explicar key-value extraction en OCI Document Understanding
- [ ] Describir normalización en OCI Speech
- [ ] Identificar cuándo usar cada servicio
- [ ] Entender los 14 tipos de entidades en NER
- [ ] Conocer los 3 niveles de análisis de sentimiento
- [ ] Explicar diferencia entre OCR en OCI Vision vs OCI Document Understanding
