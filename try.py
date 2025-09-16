import asyncio
from falkordb.asyncio.falkordb import FalkorDB

async def main():
    # 1️⃣ Connect to FalkorDB
    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph("QA_Knowledge")

    # 2️⃣ Store a Question-Answer pair
    question = "What is Graphiti?"
    answer = "Graphiti is a framework that integrates LLMs with GraphDBs like FalkorDB."
    
    await g.query(f"""
        MERGE (q:Question {{text: '{question}'}})
        MERGE (r:Result {{answer: '{answer}'}})
        MERGE (q)-[:DERIVES]->(r)
    """)
    print(f"✅ Stored Q&A: {question} -> {answer}")

    # 3️⃣ Retrieve if the same question is asked again
    asked_question = "What is Graphiti?"
    res = await g.query(f"""
        MATCH (q:Question {{text: '{asked_question}'}})-[:DERIVES]->(r:Result)
        RETURN r.answer
    """)
    
    if res.result_set:
        print("💡 Answer from FalkorDB cache:", res.result_set[0][0])
    else:
        print("🤔 No answer found, call Gemini LLM here and store it next time.")

if __name__ == "__main__":
    asyncio.run(main())
