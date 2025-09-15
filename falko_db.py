import asyncio
from falkordb.asyncio.falkordb import FalkorDB
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

GEMINI_API_KEY = "keep your gemini api key here"

async def main():
    # 1️⃣ Connect to FalkorDB asynchronously
    db = FalkorDB(host="localhost", port=6379)

    # 2️⃣ Select or create graph 'MotoGP'
    g = db.select_graph("MotoGP")

    # 3️⃣ Create nodes and relationships
    await g.query(
        """
        CREATE (:Rider {name:'Valentino Rossi'})-[:rides]->(:Team {name:'Yamaha'}),
               (:Rider {name:'Dani Pedrosa'})-[:rides]->(:Team {name:'Honda'}),
               (:Rider {name:'Andrea Dovizioso'})-[:rides]->(:Team {name:'Ducati'})
        """
    )

    print("🎉 Nodes and relationships created!")

    # 4️⃣ Query riders representing Yamaha
    res = await g.query(
        """
        MATCH (r:Rider)-[:rides]->(t:Team)
        WHERE t.name = 'Yamaha'
        RETURN r.name
        """
    )
    print("Riders representing Yamaha:")
    for row in res.result_set:
        print(row[0])

    # 5️⃣ Query count of riders in Ducati
    res = await g.query(
        """
        MATCH (r:Rider)-[:rides]->(t:Team {name:'Ducati'})
        RETURN count(r)
        """
    )
    print("Number of riders in Ducati:", res.result_set[0][0])

    # 6️⃣ Initialize Graphiti + Gemini for RAG
    graphiti = Graphiti(
        graph_driver=db,
        llm_client=GeminiClient(
            config=LLMConfig(api_key=GEMINI_API_KEY, model="gemini-2.0-flash")
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(api_key=GEMINI_API_KEY, embedding_model="embedding-001")
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(api_key=GEMINI_API_KEY, model="gemini-2.5-flash-lite-preview-06-17")
        )
    )

    print("✅ Connected to Graphiti with Gemini")

    # 7️⃣ Ingest the MotoGP graph as RAG episodes
    await graphiti.ingest_episode(
        text="Valentino Rossi rides for Yamaha",
        metadata={"type":"Rider-Team", "rider":"Valentino Rossi", "team":"Yamaha"}
    )

    await graphiti.ingest_episode(
        text="Dani Pedrosa rides for Honda",
        metadata={"type":"Rider-Team", "rider":"Dani Pedrosa", "team":"Honda"}
    )

    await graphiti.ingest_episode(
        text="Andrea Dovizioso rides for Ducati",
        metadata={"type":"Rider-Team", "rider":"Andrea Dovizioso", "team":"Ducati"}
    )

    print("🎯 MotoGP graph ingested as RAG episodes for Gemini!")

if __name__ == "__main__":
    asyncio.run(main())
