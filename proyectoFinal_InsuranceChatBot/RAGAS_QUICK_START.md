# 🚀 RAGAS Evaluation - Quick Reference

## One-Command Execution

### Jupyter Notebook
```bash
# Install dependencies
pip install ragas datasets matplotlib jupyter

# Run notebook
jupyter notebook ragas_evaluation.ipynb
```

### Python Script
```bash
# Install dependencies
pip install ragas datasets matplotlib

# Run script
python ragas_evaluation.py
```

## Prerequisites Checklist

- [ ] ChromaDB built at `backend/chroma_db/`
- [ ] `GOOGLE_API_KEY` in `.env` file
- [ ] Python 3.8+ installed
- [ ] Internet connection (for Gemini API calls)

## Quick Setup

```bash
# 1. Install all dependencies at once
pip install -r backend/requirements.txt ragas datasets matplotlib

# 2. Verify ChromaDB exists
ls backend/chroma_db/

# 3. Check API key is set
grep GOOGLE_API_KEY .env

# 4. Run evaluation
python ragas_evaluation.py  # or jupyter notebook ragas_evaluation.ipynb
```

## Expected Results (15-25 min runtime)

### Files Created
- `ragas_evaluation_results.csv` - Detailed per-question results
- `ragas_metrics_summary.csv` - Statistical summary
- `ragas_evaluation_chart.png` - Bar chart visualization (script only)

### Metrics Range (0-1 scale)
| Score | Quality |
|-------|---------|
| 0.8-1.0 | Excellent ✅ |
| 0.6-0.8 | Good 👍 |
| 0.4-0.6 | Acceptable ⚠️ |
| 0.0-0.4 | Needs improvement ❌ |

## Common Issues

### "No module named 'ragas'"
```bash
pip install ragas datasets
```

### "ChromaDB not found"
```bash
cd backend/src
python chroma_db_builder.py
```

### "GOOGLE_API_KEY not found"
```bash
# Add to .env file
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

### Slow execution
✅ Normal - RAGAS makes multiple LLM calls per metric  
⏱️ Expect 15-25 minutes for 30 questions

## Customization

### Reduce dataset size (faster testing)
Edit the script/notebook and reduce `evaluation_questions` to 5-10 items

### Adjust chatbot parameters
```python
chatbot = InsuranceChatbot(
    chroma_db_path=CHROMA_DB_PATH,
    max_context_docs=10,  # ← Adjust this
    model="gemini-2.0-flash-exp"
)
```

## Getting Help

1. 📖 **Full Guide**: `GUIA_EVALUACION_RAGAS.md` (Spanish)
2. 📄 **README**: `RAGAS_EVALUATION_README.md` (English)
3. 📊 **RAGAS Docs**: https://docs.ragas.io/
4. 🤖 **Gemini API**: https://ai.google.dev/docs

## Key Features

✅ **Non-intrusive** - Zero modifications to existing code  
✅ **Self-contained** - Includes all test data  
✅ **Well documented** - Spanish + English guides  
✅ **Multiple formats** - Notebook + Script  
✅ **Visual results** - Charts and tables

---

**Need detailed instructions?** → See `GUIA_EVALUACION_RAGAS.md`
