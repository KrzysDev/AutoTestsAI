from qdrant_client import QdrantClient, models

import os

import dotenv

dotenv.load_dotenv()

client = QdrantClient(
    url=os.getenv("CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.create_payload_index(
    collection_name="Grammar Collection",
    field_name="type",
    field_schema=models.PayloadSchemaType.KEYWORD,
)

client.delete(
    collection_name="Grammar Collection",
    points_selector=models.FilterSelector(
        filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(value="exam-task-instruction"),
                ),
            ],
        )
    ),
)