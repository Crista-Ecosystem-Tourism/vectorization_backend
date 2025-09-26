# from app.vectorizer import PlaceVectorizerV2 as PlaceVectorizer
from app.vectorizer.place_vectorizer import PlaceVectorizer
import app.config as config

vectorizer_instance = PlaceVectorizer(
    persist_dir=config.VECTOR_STORE_DIR,
    embedding_provider_name=config.EMBEDDING_PROVIDER,
    embedding_model_name=config.EMBEDDING_MODEL_NAME
)

def get_vectorizer():
    return vectorizer_instance
