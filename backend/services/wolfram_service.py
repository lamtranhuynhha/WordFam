import httpx
from typing import Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)

# Free Dictionary API - fallback for definitions
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"

async def get_wolfram_info(word: str) -> Dict[str, Optional[str]]:
    """
    Fetch word metadata (definition, etymology) from Wolfram Cloud API.
    Returns dict with definition, etymology, and usage.
    """
    wolfram_url = os.getenv('WOLFRAM_API_URL')
    
    if not wolfram_url:
        logger.warning("WOLFRAM_API_URL not set, skipping Wolfram lookup")
        return {
            "definition": None,
            "etymology": None,
            "usage": None
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{wolfram_url}?word={word}"
            
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            definitions = data.get("definitions", [])
            definition = definitions[0] if definitions else None
            
            return {
                "definition": definition,
                "etymology": data.get("etymology"),
                "usage": None  
            }
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching Wolfram data for '{word}': {e}")
        return {
            "definition": None,
            "etymology": None,
            "usage": None
        }
    except Exception as e:
        logger.error(f"Error fetching Wolfram data for '{word}': {e}")
        return {
            "definition": None,
            "etymology": None,
            "usage": None
        }

async def get_wolfram_word_family(word: str) -> Dict:
    """
    Fetch complete word family from Wolfram Cloud API.
    This offloads all computation to Wolfram (WordData, semantic similarity, etc).
    Returns full graph structure from Wolfram.
    """
    wolfram_url = os.getenv('WOLFRAM_API_URL')
    
    if not wolfram_url:
        logger.warning("WOLFRAM_API_URL not set, cannot fetch word family")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = f"{wolfram_url}?word={word}"
            
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Received Wolfram word family for '{word}': {len(data.get('nodes', []))} nodes")
            return data
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching Wolfram word family for '{word}': {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching Wolfram word family for '{word}': {e}")
        return None

def get_wolfram_info_sync(word: str) -> Dict[str, Optional[str]]:
    """
    Synchronous version of get_wolfram_info for compatibility.
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(get_wolfram_info(word))
