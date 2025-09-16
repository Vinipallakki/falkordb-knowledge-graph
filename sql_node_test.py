import asyncio
from falkordb.asyncio.falkordb import FalkorDB

async def main():
    db = FalkorDB(host="localhost", port=6379)
    g = db.select_graph("sql_node")

    # Clear old data
    await g.query("MATCH (n) DETACH DELETE n")
    print("🧹 Cleared old data in sql_node graph")

    # Q&A + SQL pairs
    qa_sql_pairs = [
        ("What were the sales in the last month?", 
         "Sales in the last month were $120,000.", 
         "SELECT SUM(sales) FROM orders WHERE month = 'August';"),

        ("What were the sales in the last week?", 
         "Sales in the last week were $32,500.", 
         "SELECT SUM(sales) FROM orders WHERE week = 36;"),

        ("What was the profit in the last month?", 
         "Profit in the last month was $45,000.", 
         "SELECT SUM(profit) FROM finance WHERE month = 'August';"),

        ("What was the profit in the last week?", 
         "Profit in the last week was $10,200.", 
         "SELECT SUM(profit) FROM finance WHERE week = 36;"),

        ("What was the loss in the last quarter?", 
         "Loss in the last quarter was $5,800.", 
         "SELECT SUM(loss) FROM finance WHERE quarter = 'Q2';"),

        ("What were the total sales this year?", 
         "Total sales this year are $950,000.", 
         "SELECT SUM(sales) FROM orders WHERE year = 2025;"),

        ("What were the total expenses this year?", 
         "Total expenses this year are $720,000.", 
         "SELECT SUM(expenses) FROM finance WHERE year = 2025;"),

        ("What is the net profit this year?", 
         "Net profit this year is $230,000.", 
         "SELECT SUM(profit) - SUM(loss) FROM finance WHERE year = 2025;"),

        ("What is the highest selling product?", 
         "The highest selling product is Product A with 15,000 units sold.", 
         "SELECT product, SUM(quantity) FROM sales GROUP BY product ORDER BY SUM(quantity) DESC LIMIT 1;"),

        ("Which region had the maximum sales?", 
         "The North region had the maximum sales with $300,000.", 
         "SELECT region, SUM(sales) FROM sales GROUP BY region ORDER BY SUM(sales) DESC LIMIT 1;")
    ]

    # Insert nodes and relationships
    for q, a, sql in qa_sql_pairs:
        query = f"""
            MERGE (ques:Question {{text: "{q}"}})
            MERGE (res:Result {{answer: "{a}"}})
            MERGE (sql:SQL {{query: "{sql}"}})
            MERGE (ques)-[:DERIVES]->(res)
            MERGE (res)-[:GENERATED_BY]->(sql)
        """
        await g.query(query)
        print(f"✅ Inserted: {q} -> {a} (SQL: {sql})")

    # Verify all data
    res = await g.query("""
        MATCH (q:Question)-[:DERIVES]->(r:Result)-[:GENERATED_BY]->(s:SQL)
        RETURN q.text, r.answer, s.query
    """)

    print("\n📌 All Q&A + SQL stored in sql_node graph:")
    for row in res.result_set:
        print(f"Q: {row[0]} | A: {row[1]} | SQL: {row[2]}")

    # 4️⃣ Ask a question (retrieval)
    user_question = "What was the profit in the last week?"

    res = await g.query(f"""
        MATCH (q:Question {{text: "{user_question}"}})-[:DERIVES]->(r:Result)-[:GENERATED_BY]->(s:SQL)
        RETURN r.answer, s.query
    """)

    if res.result_set:
        answer, sql = res.result_set[0]
        print(f"\n❓ {user_question}")
        print(f"👉 Answer: {answer}")
        print(f"🗄️ SQL: {sql}")
    else:
        print(f"\n⚠️ No stored answer found for: {user_question}")


if __name__ == "__main__":
    asyncio.run(main())
