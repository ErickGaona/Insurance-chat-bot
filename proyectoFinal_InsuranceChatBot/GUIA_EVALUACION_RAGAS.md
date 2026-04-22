# 📊 Guía de Ejecución - Evaluación RAGAS del Insurance Chatbot

Esta guía explica paso a paso cómo ejecutar el notebook de evaluación RAGAS para medir la calidad del sistema RAG del Insurance Chatbot.

---

## 🎯 Objetivo

Evaluar la calidad del sistema RAG (Retrieval-Augmented Generation) del chatbot de seguros utilizando el framework RAGAS, midiendo métricas clave como:
- **Faithfulness** (Fidelidad)
- **Answer Relevancy** (Relevancia de Respuesta)
- **Context Recall** (Recuperación de Contexto)
- **Context Precision** (Precisión de Contexto)

---

## ⚙️ Requisitos Previos

### 1. Base de Datos ChromaDB
Asegúrate de que existe la base de datos ChromaDB con los documentos de seguros:

```bash
# Verificar que existe el directorio
ls backend/chroma_db/
```

Si no existe, debes construirla primero:

```bash
cd backend/src
python chroma_db_builder.py
```

### 2. API Key de Google Gemini
Necesitas una API key válida de Google Gemini configurada en tu archivo `.env`:

```bash
# Crear archivo .env en la raíz del proyecto si no existe
cp .env.example .env

# Editar .env y agregar tu API key
GOOGLE_API_KEY=tu_api_key_aqui
```

Para obtener una API key gratuita:
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key
4. Cópiala en tu archivo `.env`

---

## 📦 Instalación de Dependencias

### Paso 1: Instalar dependencias del backend

```bash
cd backend
pip install -r requirements.txt
```

### Paso 2: Instalar RAGAS y dependencias adicionales

```bash
pip install ragas datasets matplotlib
```

**Nota:** RAGAS requiere las siguientes bibliotecas que se instalarán automáticamente:
- `langchain`
- `openai` (para embeddings)
- `datasets` (Hugging Face)

### Paso 3: Verificar instalación

```bash
python -c "import ragas; print('RAGAS version:', ragas.__version__)"
```

---

## 🚀 Ejecución del Notebook

### Opción 1: Jupyter Notebook (Recomendado)

1. **Instalar Jupyter** (si no lo tienes):
   ```bash
   pip install jupyter notebook
   ```

2. **Iniciar Jupyter Notebook**:
   ```bash
   # Desde la raíz del proyecto
   jupyter notebook
   ```

3. **Abrir el notebook**:
   - En el navegador que se abre, navega a `ragas_evaluation.ipynb`
   - Haz clic para abrirlo

4. **Ejecutar las celdas**:
   - Ejecuta cada celda secuencialmente presionando `Shift + Enter`
   - O ejecuta todas las celdas: `Cell > Run All`

### Opción 2: JupyterLab

1. **Instalar JupyterLab**:
   ```bash
   pip install jupyterlab
   ```

2. **Iniciar JupyterLab**:
   ```bash
   jupyter lab
   ```

3. **Abrir y ejecutar** el notebook `ragas_evaluation.ipynb`

### Opción 3: Google Colab

1. Sube el notebook a Google Colab
2. Sube también los archivos necesarios del proyecto
3. Modifica las rutas según sea necesario
4. Ejecuta las celdas

### Opción 4: VS Code

1. Abre VS Code en la raíz del proyecto
2. Instala la extensión "Jupyter" de Microsoft
3. Abre `ragas_evaluation.ipynb`
4. Selecciona el kernel de Python apropiado
5. Ejecuta las celdas

---

## 📋 Proceso de Evaluación

El notebook ejecuta los siguientes pasos automáticamente:

### 1. Importaciones y Configuración (Celdas 1-3)
- Importa bibliotecas necesarias
- Configura rutas y variables de entorno
- Importa módulos del chatbot

### 2. Inicialización del Chatbot (Celdas 4-5)
- Verifica la existencia de ChromaDB
- Inicializa el chatbot con la configuración apropiada
- Conecta a la API de Google Gemini

### 3. Dataset Sintético (Celda 6)
- Carga 30 preguntas predefinidas sobre seguros médicos
- Cada pregunta incluye su respuesta esperada (ground truth)

### 4. Generación de Respuestas (Celdas 7-9)
- El chatbot procesa cada pregunta
- Recupera contextos relevantes de ChromaDB
- Genera respuestas usando Google Gemini
- **⏱️ Tiempo estimado**: 5-10 minutos

### 5. Evaluación RAGAS (Celdas 10-12)
- Convierte el dataset al formato de RAGAS
- Ejecuta las 4 métricas de evaluación
- **⏱️ Tiempo estimado**: 10-15 minutos

### 6. Visualización de Resultados (Celdas 13-16)
- Muestra estadísticas resumidas
- Genera gráficos de barras
- Analiza mejores y peores respuestas
- Guarda resultados en archivos CSV

---

## 📊 Resultados Generados

Al finalizar la ejecución, se generan los siguientes archivos:

1. **`ragas_evaluation_results.csv`**
   - Resultados detallados por cada pregunta
   - Todas las métricas calculadas
   - Preguntas, respuestas y contextos

2. **`ragas_metrics_summary.csv`**
   - Resumen estadístico de las métricas
   - Promedios, desviación estándar, mínimos y máximos

3. **Gráficos en el notebook**
   - Gráfico de barras con las 4 métricas principales
   - Visualizaciones de distribución de puntuaciones

---

## 🔍 Interpretación de Resultados

### Escala de Puntuación
Todas las métricas se miden en una escala de **0 a 1**, donde:
- **0.8 - 1.0**: Excelente
- **0.6 - 0.8**: Bueno
- **0.4 - 0.6**: Aceptable
- **0.0 - 0.4**: Necesita mejora

### Qué Significa Cada Métrica

#### 1. Faithfulness (Fidelidad) - 0 a 1
- **Qué mide**: Si la respuesta está basada en el contexto recuperado
- **Valor alto (>0.8)**: La respuesta es fiel al contexto, sin "alucinaciones"
- **Valor bajo (<0.5)**: El modelo está inventando información

#### 2. Answer Relevancy (Relevancia) - 0 a 1
- **Qué mide**: Si la respuesta es relevante para la pregunta
- **Valor alto (>0.8)**: Respuesta directa y pertinente
- **Valor bajo (<0.5)**: Respuesta desviada o incompleta

#### 3. Context Recall (Recuperación) - 0 a 1
- **Qué mide**: Si el contexto recuperado contiene la información necesaria
- **Valor alto (>0.8)**: Buena recuperación de documentos relevantes
- **Valor bajo (<0.5)**: El sistema de búsqueda no encuentra información relevante

#### 4. Context Precision (Precisión) - 0 a 1
- **Qué mide**: Si los documentos más relevantes están primero en el ranking
- **Valor alto (>0.8)**: Buen ordenamiento de resultados
- **Valor bajo (<0.5)**: Documentos irrelevantes rankeados primero

---

## 🛠️ Solución de Problemas

### Error: "No module named 'ragas'"
```bash
pip install ragas datasets
```

### Error: "ChromaDB not found"
```bash
cd backend/src
python chroma_db_builder.py
```

### Error: "GOOGLE_API_KEY not found"
1. Verifica que existe el archivo `.env` en la raíz del proyecto
2. Asegúrate de que contiene: `GOOGLE_API_KEY=tu_key_aqui`
3. Reinicia el kernel del notebook

### Error: "Rate limit exceeded"
- Estás haciendo demasiadas llamadas a la API de Gemini
- Espera unos minutos e intenta de nuevo
- Considera reducir el número de preguntas en el dataset

### Ejecución muy lenta
- Normal: RAGAS realiza múltiples llamadas a LLMs para cada métrica
- Tiempo típico: 15-20 minutos para 30 preguntas
- Para pruebas rápidas: reduce `evaluation_questions` a 5-10 preguntas

### Error de memoria
- Cierra otros programas
- Reduce el número de preguntas en el dataset
- Usa un entorno con más RAM disponible

---

## 🎓 Mejores Prácticas

### 1. Primera Ejecución
- Empieza con 5-10 preguntas para verificar que todo funciona
- Luego ejecuta el dataset completo de 30 preguntas

### 2. Iteración y Mejora
1. Ejecuta la evaluación con la configuración actual
2. Analiza los resultados
3. Ajusta parámetros del chatbot:
   - `max_context_docs`: número de documentos recuperados
   - Tamaño de chunks en ChromaDB
   - System prompt del chatbot
4. Re-ejecuta la evaluación
5. Compara resultados

### 3. Personalización
- Puedes agregar tus propias preguntas al dataset
- Asegúrate de incluir el `ground_truth` (respuesta correcta)
- Mantén preguntas relevantes al dominio de seguros médicos

---

## 📈 Acciones Según Resultados

### Si Faithfulness es bajo (<0.6)
- **Problema**: El modelo está alucinando información
- **Solución**: 
  - Ajustar el system prompt para enfatizar "responder solo con el contexto"
  - Reducir la temperatura del modelo
  - Revisar la calidad de los chunks en ChromaDB

### Si Answer Relevancy es bajo (<0.6)
- **Problema**: Respuestas no relevantes a las preguntas
- **Solución**:
  - Mejorar el system prompt
  - Verificar que las preguntas estén bien formuladas
  - Ajustar el modelo de generación

### Si Context Recall es bajo (<0.6)
- **Problema**: No se recupera información relevante
- **Solución**:
  - Aumentar `max_context_docs`
  - Mejorar el chunking de documentos
  - Verificar calidad de embeddings
  - Considerar re-indexar ChromaDB

### Si Context Precision es bajo (<0.6)
- **Problema**: Documentos irrelevantes rankeados primero
- **Solución**:
  - Ajustar el algoritmo de scoring
  - Mejorar metadata de documentos
  - Considerar hybrid search (keyword + semantic)

---

## 📞 Soporte

Si encuentras problemas:
1. Verifica que todas las dependencias están instaladas
2. Revisa los logs de error en el notebook
3. Consulta la documentación de RAGAS: https://docs.ragas.io/
4. Revisa el código fuente del chatbot en `backend/src/`

---

## ✅ Checklist de Ejecución

Antes de ejecutar el notebook, verifica:

- [ ] ChromaDB construido (`backend/chroma_db/` existe)
- [ ] GOOGLE_API_KEY configurado en `.env`
- [ ] Dependencias instaladas (`ragas`, `datasets`, `matplotlib`)
- [ ] Jupyter o JupyterLab instalado
- [ ] Conexión a internet (para llamadas a API de Gemini)
- [ ] Al menos 15-20 minutos disponibles para ejecución completa

---

## 🎯 Resultados Esperados

Al finalizar exitosamente, deberías tener:

1. ✅ Tabla resumen con las 4 métricas RAGAS
2. ✅ Gráfico de barras visualizando las métricas
3. ✅ Análisis de top 5 mejores y peores respuestas
4. ✅ Archivos CSV con resultados detallados
5. ✅ Interpretación clara de la calidad del sistema RAG

---

## 📚 Recursos Adicionales

- **Documentación RAGAS**: https://docs.ragas.io/
- **Paper RAGAS**: https://arxiv.org/abs/2309.15217
- **Google Gemini Docs**: https://ai.google.dev/docs
- **ChromaDB Docs**: https://docs.trychroma.com/

---

**Nota Final**: Esta evaluación es completamente **no intrusiva**. No modifica ningún archivo del proyecto original, solo lee la configuración existente y genera nuevos archivos de resultados.
