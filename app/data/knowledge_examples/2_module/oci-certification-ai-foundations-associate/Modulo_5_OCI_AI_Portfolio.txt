# Módulo 5: Portafolio de IA de Oracle Cloud Infrastructure (OCI)

## 📋 Información del Módulo

**Peso en el examen:** 15%  
**Conceptos evaluados:**
- Descripción general de servicios de IA de OCI
- Descripción general de servicios de ML de OCI
- Descripción general de infraestructura de IA de OCI
- IA Responsable

---

## 🎯 Objetivos de Aprendizaje

Al finalizar este módulo, podrás:
1. Describir el portafolio completo de IA de Oracle
2. Comprender los servicios de IA pre-entrenados de OCI
3. Conocer los servicios de Machine Learning de OCI
4. Entender la infraestructura de IA (GPUs y Superclusters)
5. Aplicar principios de IA Responsable

---

## 1. Visión General del Stack de IA de Oracle

### Arquitectura Completa

```
┌────────────────────────────────────────┐
│  APLICACIONES (Applications)           │
│  - ERP, HCM, CX                        │
│  - Aplicaciones personalizadas         │
└────────────────────────────────────────┘
              ↑
┌────────────────────────────────────────┐
│  SERVICIOS DE IA (AI Services)         │
│  - OCI Language, OCI Vision, OCI Speech│
│  - OCI Document Understanding          │
│  - OCI Generative AI                   │
└────────────────────────────────────────┘
              ↑
┌────────────────────────────────────────┐
│  SERVICIOS DE ML (ML Services)         │
│  - OCI Data Science                    │
│  - Entrenamientos personalizados       │
└────────────────────────────────────────┘
              ↑
┌────────────────────────────────────────┐
│  INFRAESTRUCTURA DE IA                 │
│  - GPUs (A100, H100, H200, GB200)      │
│  - Superclusters                       │
│  - RDMA Networking                     │
└────────────────────────────────────────┘
              ↑
┌────────────────────────────────────────┐
│  DATOS (Data)                          │
│  - Oracle Database                     │
│  - Autonomous Database                 │
│  - MySQL HeatWave                      │
│  - Object Storage                      │
└────────────────────────────────────────┘
```

---

### Filosofía de Oracle

**"IA diseñada como experiencia perfecta, no partes sueltas"**

Oracle integra IA en **cada capa**:
- ✅ Desde la base de datos hasta las aplicaciones SaaS
- ✅ Sin necesidad de ensamblar herramientas por separado
- ✅ Integración nativa y sencilla

---

## 2. Servicios de IA de OCI (OCI AI Services)

### ¿Qué son los AI Services?

**Definición:**
Colección de servicios con **modelos de ML pre-entrenados** que facilitan construir aplicaciones de IA sin experiencia en data science.

**Características principales:**
- 🎯 Modelos pre-entrenados listos para usar
- 🔧 Opción de personalizar con tus datos
- 🚀 Sin infraestructura que gestionar
- 📞 Acceso vía API

---

### Métodos de Acceso

| Método | Descripción |
|--------|-------------|
| **OCI Console** | Interfaz web fácil de usar |
| **REST API** | Acceso programático |
| **SDKs** | Java, Python, TypeScript, .NET, Go, Ruby |
| **CLI** | Línea de comandos |

---

### Servicios Disponibles

#### 1. OCI Language

**Análisis sofisticado de texto a escala.**

**Modelos pre-entrenados:**
- ✅ Detección de idioma (75 idiomas)
- ✅ Análisis de sentimiento (general y por aspecto)
- ✅ Extracción de frases clave
- ✅ Clasificación de texto (600+ categorías)
- ✅ Reconocimiento de entidades nombradas (NER)
- ✅ Detección de información personal (PII)

**Modelos personalizados:**
- 🔧 NER personalizado
- 🔧 Clasificación personalizada

**Traducción de texto:**
- 🌍 Traducción neuronal entre múltiples idiomas

---

**Ejemplo de Análisis de Language:**

```
Input: "La película fue excelente y emocionante, 
        pero el servicio en el cine fue terrible."

Resultados:
1. Idioma detectado: Español (99.9%)

2. Sentimiento por aspecto:
   - película: Positivo (0.95)
   - servicio: Negativo (0.89)

3. Entidades:
   - "película" → PRODUCTO
   - "cine" → LUGAR

4. Clasificación: Entretenimiento > Cine

5. Frases clave: "excelente", "emocionante", "terrible"
```

---

#### 2. OCI Vision

**Procesamiento de imágenes con modelos pre-entrenados y personalizados.**

**Análisis de imágenes (pre-entrenado):**
- 📸 Detección de objetos (con bounding boxes)
- 🏷️ Clasificación de imágenes
- 📝 OCR (Reconocimiento Óptico de Caracteres)

**Modelos personalizados:**
- 🎯 Detección de objetos personalizados
- 🏷️ Clasificación personalizada

**Document Understanding:**
- 📄 Extracción de texto (OCR)
- 🔑 Extracción de pares clave-valor (recibos, facturas)
- 📊 Extracción de tablas
- 📋 Clasificación de documentos

---

**Ejemplo de Document Understanding:**

```
Input: Recibo escaneado de cafetería

Extracción:
1. Texto completo: Todo el contenido del recibo

2. Pares clave-valor:
   - merchant_name: "Example Café"
   - merchant_address: "123 Main St"
   - transaction_date: "2024-01-15"
   - transaction_time: "10:30 AM"
   - total: "$15.50"

3. Líneas de items:
   - Americano: $4.50
   - Water: $1.00

4. Tablas extraídas
```

---

#### 3. OCI Speech

**Conversión de archivos multimedia a texto.**

**Características:**
- 🎙️ Transcripción altamente precisa
- 🌐 Soporte para inglés, español y portugués
- ⚡ Procesamiento ultra rápido (horas de audio en <10 minutos)
- 📊 Puntuación automática
- 🎯 Scores de confianza (por palabra y transcripción)
- 📺 Soporte para archivos SRT (subtítulos)

**Procesamiento:**
```
Audio/Video → Speech Service → Texto transcrito
```

**Normalización:**
```
Texto literal:    "calle uno dos tres"
Texto normalizado: "Calle 123"
```

**Filtrado de obscenidades:**
- Removing: Reemplaza con asteriscos `****`
- Masking: Mantiene primera letra `f***`
- Tagging: Marca pero deja la palabra

---

#### 4. OCI Digital Assistant

**Plataforma para crear y desplegar asistentes digitales con IA.**

**Capacidades:**
- 💬 Conversaciones en lenguaje natural
- 🎯 Enrutamiento a skills apropiados
- 🔄 Manejo de interrupciones
- ❓ Desambiguación de intenciones
- 📝 Listado de capacidades

**Arquitectura:**
```
Usuario
  ↓
Digital Assistant (orquestador)
  ├─→ Skill 1 (Reservaciones)
  ├─→ Skill 2 (Facturación)
  └─→ Skill 3 (Soporte)
```

---

## 3. Servicios de ML de OCI

### OCI Data Science

**Servicio de ML end-to-end para equipos de data scientists.**

**Principios centrales:**

#### 1. Accelerated (Acelerado)
- ⚡ Acceso a poder computacional sin gestionar infraestructura
- 📚 Librerías open-source pre-instaladas
- 🚀 SDK de Oracle (Accelerated Data Science - ADS)

#### 2. Collaborative (Colaborativo)
- 👥 Compartir assets entre equipos
- 🔄 Reducir trabajo duplicado
- 📊 Reproducibilidad y auditabilidad

#### 3. Enterprise Grade (Grado Empresarial)
- 🔒 Integrado con seguridad de OCI
- 🛠️ Infraestructura completamente gestionada
- 🔄 Mantenimiento automático

---

### Componentes de OCI Data Science

#### 1. Projects (Proyectos)
**Contenedores organizacionales para equipos.**

```
Tenancy
  └── Project 1: Predicción de ventas
      ├── Notebook Session 1
      ├── Notebook Session 2
      ├── Model 1
      └── Model 2
```

---

#### 2. Notebook Sessions
**Ambiente JupyterLab interactivo.**

**Características:**
- 📓 Interfaz JupyterLab familiar
- 🐍 Python con librerías pre-instaladas
- 🖥️ Selección de compute shapes (CPU/GPU)
- 💾 Almacenamiento configurable
- 🚫 Sin aprovisionamiento manual

---

#### 3. Conda Environments
**Gestión de paquetes y ambientes.**

```
Conda Environment 1: TensorFlow 2.x
Conda Environment 2: PyTorch 1.x
Conda Environment 3: General ML
```

**Ventajas:**
- ✅ Instalación rápida de paquetes
- ✅ Gestión de dependencias
- ✅ Cambiar entre ambientes fácilmente

---

#### 4. Accelerated Data Science (ADS) SDK

**Librería de Python de Oracle que simplifica el workflow de Data Science.**

**Funciones:**
- 📊 Conectar a fuentes de datos
- 🔍 Explorar y visualizar datos
- 🤖 AutoML para entrenar modelos
- 📈 Evaluar modelos
- 🔬 Explicar modelos (XAI)
- 🔗 Acceso a Model Catalog y Object Storage

---

#### 5. Model Catalog
**Repositorio centralizado de modelos.**

**Almacena:**
- 📦 Artifacts del modelo
- 📝 Metadata (provenance, Git info)
- 📜 Scripts usados para crear el modelo

**Beneficios:**
- 👥 Compartir modelos entre equipo
- 🔄 Versionamiento
- 🔍 Trazabilidad

---

#### 6. Model Deployments
**Desplegar modelos como endpoints HTTP.**

**Flujo:**
```
Model en Catalog
      ↓
Deployment
      ↓
HTTP Endpoint
      ↓
API para predicciones en tiempo real
```

**Uso:**
```
POST https://endpoint.com/predict
{
  "features": [5.1, 3.5, 1.4, 0.2]
}

Response:
{
  "prediction": "Iris-setosa"
}
```

---

#### 7. Jobs
**Tareas de ML repetibles en infraestructura gestionada.**

**Ejemplos:**
- 🔄 Reentrenar modelo semanalmente
- 📊 Procesar datos diariamente
- 🧪 Ejecutar experimentos batch

---

### Workflow Típico en OCI Data Science

```
1. Crear Project
   ↓
2. Lanzar Notebook Session
   ↓
3. Instalar Conda Environment
   ↓
4. Desarrollar modelo (Python, ADS)
   ↓
5. Guardar en Model Catalog
   ↓
6. Desplegar como endpoint
   ↓
7. Servir predicciones en tiempo real
```

---

## 4. Infraestructura de IA de OCI

### ¿Por Qué GPUs para IA?

**CPU vs GPU:**

| Aspecto | CPU | GPU |
|---------|-----|-----|
| **Cores** | 8-64 cores potentes | Miles de cores livianos |
| **Procesamiento** | Secuencial | Paralelo masivo |
| **Uso en ML** | Inferencia simple | Entrenamiento y inferencia |
| **Velocidad ML** | Lento | 10-100x más rápido |

**Ventaja de GPU:**
```
Tarea: Multiplicar 1 millón de números

CPU (16 cores):
  Core 1: números 1-62,500
  Core 2: números 62,501-125,000
  ...
  Tiempo: ~10 segundos

GPU (5,000 cores):
  Core 1: número 1
  Core 2: número 2
  ...
  Core 5000: número 5000
  [Repite 200 veces]
  Tiempo: ~0.5 segundos
```

---

### Evolución de GPUs NVIDIA para IA

#### A100 (2020) - Arquitectura Ampere
- 🧠 Tensor Cores optimizados
- ⚡ Aceleración para deep learning

#### H100 (2022) - Arquitectura Hopper
- 🚀 Transformer Engine dedicado
- 🎯 Optimizado para LLMs

#### H200 (2024) - Hopper con más memoria
- 💾 Más memoria que H100
- 🎯 Modelos más grandes

#### B200 & GB200 (2025) - Arquitectura Blackwell
- 🌟 Rendimiento 4x de H100
- 🎯 Modelos de IA a gran escala

#### GB200 Grace Blackwell Superchip
- 🤝 2 GPUs Blackwell + 2 CPUs Grace
- 🚀 Rendimiento máximo para IA

---

### Portfolio de GPUs en OCI

| GPU | Disponibilidad | Uso Ideal |
|-----|----------------|-----------|
| **A100** | ✅ Disponible | Entrenamiento pequeño/mediano |
| **L40/L4** | ✅ Disponible | Inferencia, visualización |
| **H100** | ✅ Disponible | Entrenamiento a gran escala |
| **H200** | 📅 2025 | Modelos muy grandes |
| **B200** | 📅 2025 | Máximo rendimiento |
| **GB200** | 📅 2025 | Superclusters |

---

### OCI Superclusters

**¿Qué son?**
Clusters de decenas de miles de GPUs conectadas con **RDMA networking ultra-rápido**.

**Características:**
- 🌐 Hasta 100,000+ GPUs
- ⚡ Latencia de red ~6.5 µs (dentro de bloque)
- 📡 RDMA (Remote Direct Memory Access)
- 🔒 Aislamiento seguro entre clientes
- 🎯 Redes lossless (sin pérdida de paquetes)

---

### Arquitectura de Superclusters

```
┌─────────────────────────────────────┐
│        SUPERCLUSTER                 │
│                                     │
│  ┌────────┐  ┌────────┐  ┌────────┐ │
│  │Block 1 │  │Block 2 │  │Block n │ │
│  │        │  │        │  │        │ │
│  │ GPUs   │  │ GPUs   │  │ GPUs   │ │
│  │ Tier 1 │  │ Tier 1 │  │ Tier 1 │ │
│  │ Tier 2 │  │ Tier 2 │  │ Tier 2 │ │
│  └────────┘  └────────┘  └────────┘ │
│       ↕          ↕          ↕       │
│  ┌──────────────────────────────┐   │
│  │   Tier 3 (Spine)             │   │
│  │   Conecta todos los bloques  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Fabric de 3 niveles:**
- **Tier 1-2:** Dentro de bloque (latencia ~6.5 µs)
- **Tier 3:** Entre bloques (latencia ~20 µs)

---

### RDMA Networking

**¿Qué es RDMA?**
**Remote Direct Memory Access** permite transferencia de datos de GPU a GPU **sin usar CPU**.

```
Sin RDMA:
GPU 1 → CPU → Memoria → CPU → Red → CPU → Memoria → CPU → GPU 2
(Lento, alta latencia)

Con RDMA:
GPU 1 ──────→ Red ──────→ GPU 2
(Rápido, baja latencia)
```

**Ventajas:**
- ⚡ Latencia ultra baja
- 🚀 Alto ancho de banda
- 🔋 Baja carga en CPU

---

### Optimizaciones del Supercluster

#### 1. Buffers Ajustados
Switches configurados con buffers apropiados para manejar latencia del fabric.

#### 2. Placement Inteligente
```
Workload pequeño (HPC, Database):
  → Colocado en 1 bloque
  → Latencia ~6.5 µs ✅

Workload grande (GPU cluster):
  → Distribuido en múltiples bloques
  → Latencia promedio optimizada
```

#### 3. Network Locality Hints
```
8 GPUs distribuidas en 2 bloques:

Topología óptima:
┌─────Block 1─────┐  ┌─────Block 2─────┐
│ GPU1 ←→ GPU2    │  │ GPU5 ←→ GPU6    │
│   ↕      ↕      │  │   ↕      ↕      │
│ GPU3 ←→ GPU4    │  │ GPU7 ←→ GPU8    │
└─────────────────┘  └─────────────────┘
         ↕                    ↕
   (Tráfico local 85%)  (Tráfico local 85%)
         ↕ ←──────────────→ ↕
        (Tráfico entre bloques 15%)

Resultado:
- Mayoría de tráfico local (baja latencia)
- Menos colisiones de flujo
- Mayor throughput
```

---

### Uso de Infraestructura para LLMs

**OCI AI Quick Actions:**

```
┌────────────────────────────────┐
│  OCI Data Science              │
│                                │
│  AI Quick Actions:             │
│  ├─ Deploy LLM                 │
│  ├─ Fine-tune LLM              │
│  └─ Deploy custom model        │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  GPU Instance (H100/A100)      │
│                                │
│  Modelos soportados:           │
│  - vLLM                        │
│  - Text Generation Inference   │
│  - Text Embedding Inference    │
└────────────────────────────────┘
```

---

## 5. IA Responsable

### Principios Fundamentales

**Para que la IA sea confiable, debe ser:**

#### 1. Lawful (Legal) ⚖️
Cumplir con todas las leyes y regulaciones aplicables.

**Ejemplos:**
- GDPR (Europa)
- CCPA (California)
- Leyes de protección de datos locales
- Regulaciones sectoriales (salud, finanzas)

---

#### 2. Ethical (Ética) 🤝
Adherirse a principios éticos y valores humanos.

**Principios:**
- **Dignidad humana:** Respetar el valor intrínseco de cada persona
- **Libertad individual:** No socavar procesos democráticos
- **Igualdad:** Evitar sesgos discriminatorios
- **Derechos ciudadanos:** Proteger privacidad y derechos

---

#### 3. Robust (Robusta) 🛡️
Ser técnicamente confiable y socialmente segura.

**Aspectos:**
- Seguridad técnica
- Seguridad física
- Privacidad
- Transparencia
- Rendimiento predecible

---

### Principios Éticos de IA Responsable

#### 1. Centrada en el Humano
**IA debe ayudar a los humanos, no reemplazarlos.**

```
✅ Correcto: Sistema de IA sugiere diagnóstico
            → Médico revisa y toma decisión final

❌ Incorrecto: IA toma decisión médica final
               → Sin supervisión humana
```

---

#### 2. Justa y Sin Sesgos
**IA no debe discriminar injustamente.**

**Ejemplo de sesgo:**
```
Conjunto de datos de contratación:
- 90% hombres contratados históricamente
- 10% mujeres contratadas

Modelo entrenado con estos datos:
❌ Aprende sesgo: favorece candidatos hombres

Solución:
✅ Balancear datos
✅ Evaluar fairness
✅ Auditar regularmente
```

---

#### 3. Transparente y Explicable
**Las decisiones de IA deben ser comprensibles.**

```
Préstamo rechazado:

❌ "Préstamo rechazado por IA"
   (No explicable)

✅ "Préstamo rechazado porque:
   - Ingreso insuficiente (30%)
   - Historial crediticio limitado (50%)
   - Alta relación deuda-ingreso (20%)"
   (Explicable)
```

---

#### 4. Segura y Protegida
**IA debe ser robusta y segura.**

```
Auto autónomo:
✅ Probado en millones de escenarios
✅ Sistemas de respaldo
✅ Actualizaciones de seguridad
✅ Protección contra hacking
```

---

### Proceso de Implementación de IA Responsable

```
1. GOBERNANZA
   ├── Establecer políticas
   ├── Definir roles
   └── Crear comité de ética

2. POLÍTICAS Y PROCEDIMIENTOS
   ├── Guidelines de desarrollo
   ├── Procesos de revisión
   └── Estándares de documentación

3. IMPLEMENTACIÓN
   ├── Desarrolladores siguen políticas
   ├── Deployers implementan controles
   └── Usuarios finales capacitados

4. MONITOREO Y EVALUACIÓN
   ├── Auditorías regulares
   ├── Métricas de fairness
   └── Revisión de incidentes
```

---

### Desafíos en IA Responsable

#### Ejemplo: IA en Salud

**Desafío 1: Fairness**
```
Sistema de diagnóstico de cáncer de piel:
❌ Entrenado principalmente con imágenes de piel clara
❌ Menor precisión en tonos de piel oscuros

Solución:
✅ Datos representativos de todas las etnias
✅ Evaluación de desempeño por grupo demográfico
```

**Desafío 2: Transparencia**
```
Sistema predice riesgo de enfermedad:
❌ Algoritmo de "caja negra"
❌ Médicos no entienden por qué

Solución:
✅ Modelos interpretables
✅ Explicaciones de decisiones (SHAP, LIME)
```

**Desafío 3: Evaluación**
```
✅ Evaluación continua
✅ No causar daño al paciente
✅ Actualizar modelos regularmente
```

---

## 📝 Preguntas de Práctica para el Examen

### Pregunta 1
**¿Cuál NO es un servicio de IA de OCI?**

- ○ Speech
- ○ Language
- ○ Vision
- ✅ Translator

**Explicación:** "Translator" no es un servicio standalone. La traducción es parte de OCI Language.

---

### Pregunta 2
**¿Qué característica de OCI Data Science permite usar modelos catalogados como endpoints HTTP en infraestructura completamente gestionada?**

- ○ Jobs
- ✅ Model Deployments
- ○ Model Catalog
- ○ Conda Environments

**Explicación:** Model Deployments despliega modelos como endpoints HTTP para predicciones en tiempo real.

---

### Pregunta 3
**¿Cuál es la ventaja de usar OCI Superclusters para workloads de IA?**

- ○ Ofrecen integración con redes sociales
- ○ Son ideales para tareas como conversión texto-a-voz
- ○ Proveen solución económica para tareas simples de IA
- ✅ Entregan rendimiento y escalabilidad excepcionales para tareas complejas de IA

**Explicación:** Superclusters están diseñados para workloads demandantes que requieren poder computacional y escalabilidad masivos.

---

## 🎓 Consejos para el Examen

### Servicios de IA de OCI

| Servicio | Función | Ejemplo |
|----------|---------|---------|
| **Language** | Análisis de texto | Sentimiento, NER |
| **Vision** | Análisis de imágenes | OCR, detección objetos |
| **OCI Speech** | Audio a texto | Transcripción |
| **OCI Document Understanding** | Extracción de docs | Facturas, recibos |

### OCI Data Science - Componentes

| Componente | Función |
|------------|---------|
| **Projects** | Contenedor organizacional |
| **Notebooks** | Desarrollo interactivo |
| **Model Catalog** | Repositorio de modelos |
| **Deployments** | Endpoints HTTP |
| **Jobs** | Tareas repetibles |

### GPUs por Caso de Uso

| GPU | Mejor para |
|-----|-----------|
| **A100** | Pequeño/mediano entrenamiento |
| **H100** | Gran escala entrenamiento LLM |
| **GB200** | Máximo rendimiento, superclusters |

### IA Responsable

**Recuerda:** Legal + Ética + Robusta = IA Confiable

---

## 📚 Resumen del Módulo

| Concepto | Puntos Clave |
|----------|--------------|
| **AI Services** | Modelos pre-entrenados sin gestión de infraestructura |
| **Data Science** | Servicio ML end-to-end con JupyterLab |
| **Superclusters** | Decenas de miles de GPUs con RDMA |
| **RDMA** | Networking ultra-rápido para GPUs |
| **IA Responsable** | Legal, ética y robusta |

---

## ✅ Checklist de Preparación

Antes de avanzar, asegúrate de poder:

- [ ] Enumerar los servicios de IA de OCI
- [ ] Describir capacidades de OCI Language, OCI Vision, OCI Speech
- [ ] Explicar componentes de OCI Data Science
- [ ] Entender diferencias entre GPUs (A100, H100, GB200)
- [ ] Explicar qué son los Superclusters
- [ ] Describir RDMA networking
- [ ] Enumerar los 3 principios de IA Responsable