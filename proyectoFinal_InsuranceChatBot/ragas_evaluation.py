#!/usr/bin/env python3
"""
RAGAS Evaluation Script for Insurance Chatbot
==============================================

This is a standalone Python script version of the ragas_evaluation.ipynb notebook.
It can be executed directly from the command line.

Usage:
    python ragas_evaluation.py

Requirements:
    - ChromaDB built at backend/chroma_db/
    - GOOGLE_API_KEY set in .env file
    - Dependencies: ragas, datasets, matplotlib, pandas
"""

import os
import sys
import pandas as pd
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Add backend/src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Load environment variables
load_dotenv()

print("=" * 70)
print("📊 EVALUACIÓN RAGAS DEL INSURANCE CHATBOT")
print("=" * 70)
print()

# Import RAGAS
try:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision
    )
    print("✅ RAGAS importado correctamente")
except ImportError as e:
    print(f"❌ Error al importar RAGAS: {e}")
    print("\nPor favor instala las dependencias:")
    print("  pip install ragas datasets matplotlib")
    sys.exit(1)

# Import chatbot modules
try:
    from insurance_chatbot import InsuranceChatbot
    from chroma_rag_core import ChromaRAGCore
    print("✅ Módulos del chatbot importados correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulos del chatbot: {e}")
    sys.exit(1)

# Configure paths
CHROMA_DB_PATH = os.path.join(os.getcwd(), 'backend', 'chroma_db')

# Verify ChromaDB exists
if not os.path.exists(CHROMA_DB_PATH):
    print(f"❌ No se encontró ChromaDB en: {CHROMA_DB_PATH}")
    print("\nPor favor ejecuta primero:")
    print("  cd backend/src")
    print("  python chroma_db_builder.py")
    sys.exit(1)

print(f"✅ ChromaDB encontrado en: {CHROMA_DB_PATH}")

# Initialize chatbot
print("\n🔄 Inicializando chatbot...")
try:
    chatbot = InsuranceChatbot(
        chroma_db_path=CHROMA_DB_PATH,
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        model="gemini-2.0-flash-exp",
        max_context_docs=10
    )
    print("✅ Chatbot inicializado correctamente\n")
except Exception as e:
    print(f"❌ Error al inicializar chatbot: {e}")
    sys.exit(1)

# Define evaluation dataset
evaluation_questions = [
    {
        "question": "¿Qué gastos médicos están cubiertos en caso de hospitalización?",
        "ground_truth": "La póliza cubre gastos de días cama hospitalización, servicios hospitalarios, honorarios médicos quirúrgicos, prótesis quirúrgicas y servicio de rescate o traslado secundario durante una hospitalización quirúrgica de emergencia."
    },
    {
        "question": "¿Cuál es el período de duración del reembolso después de un evento?",
        "ground_truth": "El período de duración de reembolso se cuenta desde la fecha de ocurrencia del evento y su extensión se determina en las Condiciones Particulares de la Póliza. Los gastos que se originen después de este período no serán reembolsados."
    },
    {
        "question": "¿Qué son las prótesis quirúrgicas y están cubiertas?",
        "ground_truth": "Las prótesis quirúrgicas son gastos por prótesis fijas o removibles requeridas a consecuencia de una intervención quirúrgica. Están cubiertas, pero se excluyen las prótesis maxilofaciales."
    },
    {
        "question": "¿Cuándo se excluyen las cirugías de la cobertura?",
        "ground_truth": "Se excluyen aquellas cirugías donde el proceso diagnóstico entre la consulta médica y la cirugía tiene una duración mayor a 48 horas y cuando la estadía hospitalaria sea menor a doce horas de día cama."
    },
    {
        "question": "¿Qué requisitos deben cumplirse para obtener un reembolso?",
        "ground_truth": "Los requisitos copulativos son: 1) El evento debe ocurrir durante la vigencia, 2) Gastos dentro del período de reembolso, 3) Superar el deducible, 4) No exceder el monto máximo reembolsable, 5) No provenir de causas excluidas, 6) Prestaciones entregadas por prestadores indicados."
    },
    {
        "question": "¿Qué es el deducible en el contexto del seguro?",
        "ground_truth": "El deducible es el monto de gastos que debe superarse para que la compañía aseguradora realice reembolsos. Este valor se establece en las Condiciones Particulares de la Póliza."
    },
    {
        "question": "¿Cómo funciona el reembolso complementario con otros sistemas de salud?",
        "ground_truth": "La compañía aseguradora reembolsa o paga directamente al prestador de salud como complemento de lo que cubra el sistema previsional (Isapres, Fonasa, Cajas de Previsión, etc.), una vez otorgada y pagada la cobertura de estos sistemas."
    },
    {
        "question": "¿Qué incluyen los servicios hospitalarios cubiertos?",
        "ground_truth": "Los servicios hospitalarios incluyen derecho de pabellón, unidad de tratamiento intensivo, exámenes de laboratorio y radiología, insumos, medicamentos y otras prestaciones médicas suministradas durante la hospitalización, debidamente prescritas por el médico tratante."
    },
    {
        "question": "¿Qué son los honorarios médicos quirúrgicos?",
        "ground_truth": "Son los honorarios de médicos, paramédicos y arsenaleras que intervienen en una operación quirúrgica de las enfermedades cubiertas por el seguro."
    },
    {
        "question": "¿Qué pasa si se alcanza el monto máximo de gastos reembolsables?",
        "ground_truth": "Si la suma de los reembolsos alcanza el Monto Máximo de Gastos Reembolsables durante el período de vigencia o vence el Período de Duración de Reembolso, el asegurado no tendrá derecho a reembolso alguno por el período que reste."
    }
]

print(f"📋 Dataset de evaluación creado con {len(evaluation_questions)} preguntas\n")

# Function to get chatbot response with context
def get_chatbot_response_with_context(question, chatbot):
    """Get chatbot response with retrieved context."""
    result = chatbot.chat(question, verbose=True)
    
    contexts = []
    if 'context_docs' in result:
        for doc in result['context_docs']:
            contexts.append(doc['content'])
    
    return {
        'answer': result['answer'],
        'contexts': contexts
    }

# Generate responses and contexts
print("🔄 Generando respuestas del chatbot...\n")
ragas_dataset = []

for i, item in enumerate(evaluation_questions, 1):
    print(f"  [{i}/{len(evaluation_questions)}] {item['question'][:60]}...")
    
    try:
        response_data = get_chatbot_response_with_context(item['question'], chatbot)
        
        ragas_dataset.append({
            'question': item['question'],
            'answer': response_data['answer'],
            'contexts': response_data['contexts'],
            'ground_truth': item['ground_truth']
        })
        
        print(f"      ✅ ({len(response_data['contexts'])} contextos)\n")
        
    except Exception as e:
        print(f"      ❌ Error: {e}\n")
        continue

print(f"\n✅ Dataset completo con {len(ragas_dataset)} muestras\n")

# Convert to Hugging Face Dataset
print("🔄 Convirtiendo a formato RAGAS...")
ragas_hf_dataset = Dataset.from_list(ragas_dataset)
print("✅ Dataset convertido\n")

# Configure RAGAS metrics
metrics = [
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
]

print("📊 Métricas configuradas:")
for metric in metrics:
    print(f"  - {metric.name}")

# Run RAGAS evaluation
print("\n🔄 Ejecutando evaluación RAGAS...")
print("⏱️  Esto puede tardar 10-15 minutos...\n")

try:
    results = evaluate(
        ragas_hf_dataset,
        metrics=metrics
    )
    print("\n✅ Evaluación completada\n")
except Exception as e:
    print(f"\n❌ Error durante evaluación: {e}")
    sys.exit(1)

# Display results
print("=" * 70)
print("📊 RESULTADOS DE LA EVALUACIÓN RAGAS")
print("=" * 70)
print()

# Convert to DataFrame
results_df = results.to_pandas()

# Calculate summary statistics
metrics_summary = {
    'Métrica': [],
    'Promedio': [],
    'Desv. Est.': [],
    'Mínimo': [],
    'Máximo': []
}

metric_columns = ['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']

for metric in metric_columns:
    if metric in results_df.columns:
        metrics_summary['Métrica'].append(metric.replace('_', ' ').title())
        metrics_summary['Promedio'].append(f"{results_df[metric].mean():.4f}")
        metrics_summary['Desv. Est.'].append(f"{results_df[metric].std():.4f}")
        metrics_summary['Mínimo'].append(f"{results_df[metric].min():.4f}")
        metrics_summary['Máximo'].append(f"{results_df[metric].max():.4f}")

summary_df = pd.DataFrame(metrics_summary)
print(summary_df.to_string(index=False))
print()

# Save results
output_file = 'ragas_evaluation_results.csv'
results_df.to_csv(output_file, index=False)
print(f"✅ Resultados guardados en: {output_file}")

summary_file = 'ragas_metrics_summary.csv'
summary_df.to_csv(summary_file, index=False)
print(f"✅ Resumen guardado en: {summary_file}")

# Create visualization
print("\n🔄 Generando visualización...")

try:
    import matplotlib.pyplot as plt
    
    metric_names = [m.replace('_', ' ').title() for m in metric_columns if m in results_df.columns]
    metric_values = [results_df[m].mean() for m in metric_columns if m in results_df.columns]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(metric_names, metric_values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    plt.xlabel('Métricas RAGAS', fontsize=12, fontweight='bold')
    plt.ylabel('Puntuación (0-1)', fontsize=12, fontweight='bold')
    plt.title('Evaluación RAGAS del Insurance Chatbot', fontsize=14, fontweight='bold')
    plt.ylim(0, 1)
    plt.grid(axis='y', alpha=0.3)
    
    for bar, value in zip(bars, metric_values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 f'{value:.4f}',
                 ha='center', va='bottom', fontweight='bold')
    
    output_plot = 'ragas_evaluation_chart.png'
    plt.tight_layout()
    plt.savefig(output_plot, dpi=150, bbox_inches='tight')
    print(f"✅ Gráfico guardado en: {output_plot}")
    
except ImportError:
    print("⚠️  Matplotlib no disponible, saltando visualización")

# Final summary
print("\n" + "=" * 70)
print("✅ EVALUACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 70)
print()
print("Archivos generados:")
print(f"  1. {output_file} - Resultados detallados")
print(f"  2. {summary_file} - Resumen de métricas")
if 'output_plot' in locals():
    print(f"  3. {output_plot} - Gráfico de barras")
print()
print("Para más información, consulta: GUIA_EVALUACION_RAGAS.md")
print()
