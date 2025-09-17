import os
import asyncio
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

# Load environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
API_KEY = os.getenv("GEMINI_API_KEY", "<your-google-api-key>")

# Initialize Graphiti
graphiti = Graphiti(
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    llm_client=GeminiClient(config=LLMConfig(api_key=API_KEY, model="gemini-2.0-flash")),
    embedder=GeminiEmbedder(config=GeminiEmbedderConfig(api_key=API_KEY, embedding_model="embedding-001")),
    cross_encoder=GeminiRerankerClient(config=LLMConfig(api_key=API_KEY, model="gemini-2.5-flash-lite-preview-06-17"))
)

print("✅ Connected to Neo4j + Graphiti with Gemini!")

driver = graphiti.driver  # use Neo4j driver directly

# QA + SQL pairs
qa_sql_pairs = [
    ("What were the sales in the last month?", "Sales in the last month were $120,000.", "SELECT SUM(sales) FROM orders WHERE month = 'August';"),
    ("What were the sales in the last week?", "Sales in the last week were $32,500.", "SELECT SUM(sales) FROM orders WHERE week = 36;"),
    ("What was the profit in the last month?", "Profit in the last month was $45,000.", "SELECT SUM(profit) FROM finance WHERE month = 'August';"),
    ("What was the profit in the last week?", "Profit in the last week was $10,200.", "SELECT SUM(profit) FROM finance WHERE week = 36;"),
    ("What was the loss in the last quarter?", "Loss in the last quarter was $5,800.", "SELECT SUM(loss) FROM finance WHERE quarter = 'Q2';"),
    ("What were the total sales this year?", "Total sales this year are $950,000.", "SELECT SUM(sales) FROM orders WHERE year = 2025;"),
    ("What were the total expenses this year?", "Total expenses this year are $720,000.", "SELECT SUM(expenses) FROM finance WHERE year = 2025;"),
    ("What is the net profit this year?", "Net profit this year is $230,000.", "SELECT SUM(profit) - SUM(loss) FROM finance WHERE year = 2025;"),
    ("What is the highest selling product?", "The highest selling product is Product A with 15,000 units sold.", "SELECT product, SUM(quantity) FROM sales GROUP BY product ORDER BY SUM(quantity) DESC LIMIT 1;"),
    ("Which region had the maximum sales?", "The North region had the maximum sales with $300,000.", "SELECT region, SUM(sales) FROM sales GROUP BY region ORDER BY SUM(sales) DESC LIMIT 1;")
]

# Insert QA + SQL nodes
async def insert_qa_sql():
    async with driver.session(database="neo4j") as session:
        # Clear old data
        await session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))

        # Insert QA + SQL nodes
        for q, a, sql in qa_sql_pairs:
            await session.execute_write(lambda tx: tx.run(
                """
                MERGE (ques:Question {text: $q})
                MERGE (res:Result {answer: $a})
                MERGE (sql:SQL {query: $sql})
                MERGE (ques)-[:DERIVES]->(res)
                MERGE (res)-[:GENERATED_BY]->(sql)
                """, q=q, a=a, sql=sql
            ))
            print(f"✅ Inserted: {q} -> {a}")

# Ask a question
# Ask a question
# Ask a question
async def ask_question(question_text):
    async with driver.session(database="neo4j") as session:
        async def fetch_answer(tx):
            result = await tx.run(
                "MATCH (ques:Question {text: $q})-[:DERIVES]->(res:Result) "
                "RETURN res.answer AS answer",
                q=question_text
            )
            record = await result.single()  # await here, after tx.run
            return record

        record = await session.execute_read(fetch_answer)

        if record:
            print(f"\n❓ Question: {question_text}")
            print(f"💡 Answer: {record['answer']}")
        else:
            print(f"\n❓ Question: {question_text}")
            print("⚠️ Answer not found in the graph.")



# Main flow
async def main():
    # Insert all QA + SQL nodes
    await insert_qa_sql()

    # Ask a few questions
    await ask_question("What was the profit in the last week?")
    await ask_question("Which region had the maximum sales?")

# Run the async main
if __name__ == "__main__":
    asyncio.run(main())
