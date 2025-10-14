import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
env_loaded = load_dotenv()
logger = logging.getLogger(__name__)

if env_loaded:
    logger.info("✅ .env file loaded successfully")
else:
    logger.warning("❌ .env file not found or not loaded")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Service configuration
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8000")
LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "https://llmgateway.qburst.build")
LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# Log configuration status
logger.info(f"Search service URL: {SEARCH_SERVICE_URL}")
logger.info(f"LLM Gateway URL: {LLM_GATEWAY_URL}")
logger.info(f"LLM API Key present: {bool(LLM_API_KEY)}")
logger.info(f"Model: {MODEL_NAME}")

# Debug: Show if API key is loaded (don't log the actual key)
if LLM_API_KEY:
    logger.info(f"LLM API Key length: {len(LLM_API_KEY)} characters")
    logger.info("✅ LLM is fully configured and ready to use")
else:
    logger.warning("❌ LLM API Key is missing - using fallback responses")
