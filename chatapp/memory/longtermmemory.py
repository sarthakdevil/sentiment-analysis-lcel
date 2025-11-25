from langgraph.store.memory import InMemoryStore
from chatapp.models import ExtractedMemory
from langchain.tools import ToolRuntime,tool
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

store = InMemoryStore()

@dataclass
class Context:
    user_id: int = 0

@tool
def save_memory(memory: ExtractedMemory, runtime: ToolRuntime[Context]) -> str:
    """
    Save extracted memory to the store associated with the user.
    
    Args:
        memory: The extracted memory dictionary.
        runtime: The tool runtime containing context.
    
    Returns:
        Confirmation message.
    
    Raises:
        ValueError: If user_id is missing from context.
    """
    try:

        if not runtime.context or not hasattr(runtime.context, 'user_id'):
            raise ValueError("Runtime context must contain user_id")
        
        user_id = runtime.context.user_id
        
        if not user_id:
            raise ValueError("user_id cannot be empty")

        store_instance = runtime.store

        existing = store_instance.get(("users",), user_id)

        memory_dict = memory if isinstance(memory, dict) else memory.__dict__
        
        if existing and existing.value:

            merged = {**existing.value, **memory_dict}
            store_instance.put(("users",), user_id, merged)
            logger.info(f"Updated memory for user {user_id}")
            return f"Updated memory for user {user_id}: {list(memory_dict.keys())}"
        else:

            store_instance.put(("users",), user_id, memory_dict)
            logger.info(f"Created new memory for user {user_id}")
            return f"Stored new memory for user {user_id}: {list(memory_dict.keys())}"
            
    except Exception as e:
        logger.error(f"Failed to save memory: {e}")
        raise