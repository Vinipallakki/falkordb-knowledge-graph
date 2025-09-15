# falkordb-knowledge-graph
# 🚀 FalkorDB + Gemini + Graphiti RAG Demo

This project is a simple **MotoGP Knowledge Graph** built on **FalkorDB** and integrated with **Google Gemini** using **Graphiti**.
It demonstrates how to combine **graph databases** with **LLMs** for Retrieval-Augmented Generation (RAG).

---

## 📌 Features

* Models MotoGP riders and their teams as a graph (`(:Rider)-[:rides]->(:Team)`)
* Runs queries on FalkorDB (e.g., riders in Yamaha, number of Ducati riders)
* Integrates Gemini (LLM, embeddings, reranker) with Graphiti for RAG ingestion
* Ingests structured graph data as episodes for AI reasoning

---

## ⚙️ Requirements

* Python 3.12+
* FalkorDB running locally (default: `localhost:6379`)
* Google Gemini API key

Install dependencies:

```bash
pip install falkordb graphiti-core
```

---

## ▶️ Running the Demo

1. **Start FalkorDB**

   ```bash
   docker run -p 6379:6379 falkordb/falkordb
   ```

2. **Set your Gemini API key**
   Replace inside `trys.py`:

   ```python
   GEMINI_API_KEY = "your-gemini-api-key"
   ```

3. **Run the script**

   ```bash
   python trys.py
   ```

---

## 📖 Example Output

```
🎉 Nodes and relationships created!
Riders representing Yamaha:
Valentino Rossi
Number of riders in Ducati: 1
✅ Connected to Graphiti with Gemini
🎯 MotoGP graph ingested as RAG episodes for Gemini!
```

---

## 🧩 Tech Stack

* **FalkorDB** → Graph database
* **Graphiti** → RAG orchestration
* **Google Gemini** → LLM, embeddings, reranker

---

## 💡 Next Steps

* Extend the graph with more riders & teams
* Query Gemini with natural language questions
* Experiment with hybrid retrieval (graph + semantic search)

---

Would you like me to also add a **section with a query example using `graphiti.query("Who rides for Yamaha?")`** so it feels more complete as a RAG workflow, not just ingestion?
