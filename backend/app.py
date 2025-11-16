from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models.response import GraphResponse
from services.graph_builder import build_word_family_graph
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WordFam API",
    description="Generate word family graphs using NLP",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Starting WordFam API...")
    
    # Ensure NLTK data is available
    from services.wordnet_engine import ensure_wordnet
    ensure_wordnet()
    
    # Pre-load the embedding model
    from services.embedding_engine import get_model
    logger.info("Loading embedding model...")
    get_model()
    
    logger.info("WordFam API ready!")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "WordFam API",
        "version": "1.0.0",
        "endpoints": {
            "family": "/api/family?word={word}"
        }
    }

@app.get("/api/family", response_model=GraphResponse)
async def get_word_family(
    word: str = Query(..., description="The root word to analyze", min_length=1, max_length=50)
):
    """
    Generate a word family graph for the given word.
    
    - **word**: The root word to analyze (required)
    
    Returns a graph structure with nodes, edges, and metadata.
    """
    try:
        word = word.strip().lower()
        
        if not word:
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        
        if not word.isalpha():
            raise HTTPException(status_code=400, detail="Word must contain only letters")
        
        logger.info(f"Processing request for word: {word}")
        
        graph = await build_word_family_graph(word)
        
        return graph
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing word '{word}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
