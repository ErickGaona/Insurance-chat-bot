# 📊 RAGAS Evaluation - Insurance Chatbot

## 🎯 Objetivo

Este directorio contiene la implementación de evaluación RAGAS (Retrieval-Augmented Generation Assessment) para medir la calidad del sistema RAG del Insurance Chatbot.

## 📁 Archivos Incluidos

### 1. `ragas_evaluation.ipynb` 
**Notebook de Evaluación RAGAS**

Notebook Jupyter completo y ejecutable que:
- Inicializa el chatbot de seguros médicos
- Genera un dataset sintético de 30 preguntas sobre pólizas de seguros
- Obtiene respuestas y contextos del sistema RAG
- Calcula métricas RAGAS:
  - **Faithfulness** (Fidelidad): Mide si la respuesta es fiel al contexto
  - **Answer Relevancy** (Relevancia): Evalúa la pertinencia de la respuesta
  - **Context Recall** (Recuperación): Mide la calidad de recuperación de contexto
  - **Context Precision** (Precisión): Evalúa el ranking de documentos recuperados
- Visualiza resultados con tablas y gráficos
- Guarda resultados en archivos CSV

### 2. `GUIA_EVALUACION_RAGAS.md`
**Guía de Ejecución (En Español)**

Documentación completa que incluye:
- Requisitos previos y configuración
- Instalación paso a paso de dependencias
- Instrucciones de ejecución del notebook
- Interpretación de resultados y métricas
- Solución de problemas comunes
- Mejores prácticas y recomendaciones

## 🚀 Inicio Rápido

### Instalación de Dependencias

```bash
# Instalar dependencias del backend
cd backend
pip install -r requirements.txt

# Instalar RAGAS y bibliotecas adicionales
pip install ragas datasets matplotlib
```

### Configuración

1. **Verificar ChromaDB**: Asegúrate de que existe `backend/chroma_db/`
2. **API Key**: Configura `GOOGLE_API_KEY` en el archivo `.env`

### Ejecución

```bash
# Desde la raíz del proyecto
jupyter notebook ragas_evaluation.ipynb
```

O usa JupyterLab, VS Code, o Google Colab.

## 📊 Métricas Evaluadas

| Métrica | Descripción | Rango |
|---------|-------------|-------|
| **Faithfulness** | Fidelidad de la respuesta al contexto recuperado | 0-1 |
| **Answer Relevancy** | Relevancia de la respuesta a la pregunta | 0-1 |
| **Context Recall** | Calidad de recuperación del contexto relevante | 0-1 |
| **Context Precision** | Precisión del ranking de documentos | 0-1 |

**Interpretación**: 
- **0.8-1.0**: Excelente
- **0.6-0.8**: Bueno  
- **0.4-0.6**: Aceptable
- **0.0-0.4**: Necesita mejora

## 🔍 Características Clave

### ✅ No Intrusivo
- **Cero modificaciones** al código existente del chatbot
- Solo lectura de configuraciones y datos existentes
- Genera nuevos archivos de resultados sin alterar el proyecto

### ✅ Completo y Autónomo
- Dataset sintético incluido (30 preguntas)
- Todas las dependencias claramente especificadas
- Ejecutable de forma local, sin Docker

### ✅ Bien Documentado
- Comentarios detallados en cada celda
- Guía completa en español
- Interpretación clara de resultados

## 📈 Resultados Generados

Al ejecutar el notebook, se crean:

1. **`ragas_evaluation_results.csv`**: Resultados detallados por pregunta
2. **`ragas_metrics_summary.csv`**: Resumen estadístico de métricas
3. **Visualizaciones**: Gráficos de barras y análisis comparativos

## 🛠️ Solución de Problemas

### Error común: "No module named 'ragas'"
```bash
pip install ragas datasets
```

### Error: "ChromaDB not found"
```bash
cd backend/src
python chroma_db_builder.py
```

### Error: "GOOGLE_API_KEY not found"
Verifica que el archivo `.env` contenga:
```
GOOGLE_API_KEY=tu_api_key_aqui
```

Para más detalles, consulta `GUIA_EVALUACION_RAGAS.md`

## 📚 Dataset de Evaluación

El notebook incluye **30 preguntas sintéticas** sobre:
- Coberturas de hospitalización
- Requisitos de reembolso
- Exclusiones de pólizas
- Períodos de duración
- Servicios médicos cubiertos
- Prótesis quirúrgicas
- Sistema de deducibles

Cada pregunta incluye:
- `question`: La pregunta del usuario
- `ground_truth`: Respuesta correcta esperada
- `answer`: Respuesta generada por el chatbot (calculada)
- `contexts`: Contextos recuperados de ChromaDB (calculados)

## ⏱️ Tiempo de Ejecución

- **Generación de respuestas**: ~5-10 minutos (30 preguntas)
- **Evaluación RAGAS**: ~10-15 minutos (4 métricas)
- **Total estimado**: 15-25 minutos

## 🎓 Uso Recomendado

1. **Primera ejecución**: Usa el dataset completo de 30 preguntas
2. **Análisis**: Revisa métricas y identifica áreas de mejora
3. **Iteración**: Ajusta parámetros del chatbot (max_context_docs, system prompt, etc.)
4. **Re-evaluación**: Ejecuta nuevamente para comparar resultados
5. **Optimización**: Repite el ciclo hasta alcanzar métricas satisfactorias

## 🔗 Referencias

- **RAGAS Framework**: https://docs.ragas.io/
- **RAGAS Paper**: https://arxiv.org/abs/2309.15217
- **ChromaDB**: https://docs.trychroma.com/
- **Google Gemini**: https://ai.google.dev/docs

## 📝 Notas Importantes

- Requiere conexión a internet (llamadas a API de Gemini para evaluación)
- La evaluación usa el mismo modelo (Gemini) tanto para generación como para métricas RAGAS
- Los resultados son deterministas para el mismo dataset y configuración
- **Constraint crítica**: NO se modifica ningún archivo del repositorio original

---

**Autor**: AI Agent - Copilot  
**Fecha**: 2024  
**Proyecto**: Insurance Chatbot RAG Evaluation  
**Framework**: RAGAS (Retrieval-Augmented Generation Assessment)
