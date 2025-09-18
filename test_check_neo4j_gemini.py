import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

# Gemini clients
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

################################################
# CONFIGURATION
################################################

logging.basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

# Neo4j Aura connection
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://ee7f18d0.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv(
    "NEO4J_PASSWORD",
    "0mbpF0Vcqwhn6MndRBfos9J1s8hHo99RUZruOaV2vu8",
)
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Gemini API Key
API_KEY = os.getenv("GEMINI_API_KEY", "")

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set")


async def main():
    #################################################
    # INITIALIZATION WITH GEMINI
    #################################################
    graphiti = Graphiti(
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD,
        llm_client=GeminiClient(
            config=LLMConfig(api_key=API_KEY, model="gemini-2.0-flash")
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=API_KEY, embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=API_KEY,
                model="gemini-2.5-flash-lite-preview-06-17",
            )
        ),
    )

    try:
        # Initialize indices and constraints
        await graphiti.build_indices_and_constraints()

        #################################################
        # ADDING BUSINESS EPISODES
        #################################################
        episodes = [
            {
                "content": "The sales in the last month were $120,000.",
                "type": EpisodeType.text,
                "description": "financial report",
            },
            {
                "content": "The sales in the last year were $1.5 million.",
                "type": EpisodeType.text,
                "description": "financial report",
            },
            {
                "content": "The company made a profit of $300,000 last year.",
                "type": EpisodeType.text,
                "description": "financial report",
            },
            {
                "content": "The company had a loss of $50,000 in the second quarter of 2023.",
                "type": EpisodeType.text,
                "description": "financial report",
            },
            {
                "content": {
                    "quarter": "Q1 2024",
                    "sales": "$400,000",
                    "profit": "$80,000",
                },
                "type": EpisodeType.json,
                "description": "quarterly structured report",
            },
            {
                "content": {
                    "quarter": "Q2 2024",
                    "sales": "$350,000",
                    "loss": "$20,000",
                },
                "type": EpisodeType.json,
                "description": "quarterly structured report",
            },
        ]

        for i, episode in enumerate(episodes):
            await graphiti.add_episode(
                name=f"Financial Report {i}",
                episode_body=episode["content"]
                if isinstance(episode["content"], str)
                else json.dumps(episode["content"]),
                source=episode["type"],
                source_description=episode["description"],
                reference_time=datetime.now(timezone.utc),
            )
            print(
                f"✅ Added episode: Financial Report {i} ({episode['type'].value})"
            )

        #################################################
        # BUSINESS QUERIES
        #################################################
        queries = [
            "What is the sales in the last month?",
        ]

        for q in queries:
            print(f"\n🔎 Searching for: '{q}'")
            results = await graphiti.search(q)

        if results:
            best_result = results[0]  # ✅ only the first, most relevant
            print(f"✅ Answer: {best_result.fact}")
        else:
            print("⚠️ No results found.")


    finally:
        await graphiti.close()
        print("\n🔌 Connection closed")


if __name__ == "__main__":
    asyncio.run(main())
