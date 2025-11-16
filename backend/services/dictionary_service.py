import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def get_word_definition(word: str) -> Optional[str]:
    """
    Get word definition from Free Dictionary API.
    Returns the first definition found, or None if not available.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    entry = data[0]
                    
                    if 'meanings' in entry and len(entry['meanings']) > 0:
                        meaning = entry['meanings'][0]
                        
                        if 'definitions' in meaning and len(meaning['definitions']) > 0:
                            definition = meaning['definitions'][0].get('definition', '')
                            
                            pos = meaning.get('partOfSpeech', '')
                            if pos and definition:
                                return f"({pos}) {definition}"
                            return definition
            
            return None
            
    except Exception as e:
        logger.debug(f"Failed to get definition for '{word}': {e}")
        return None
