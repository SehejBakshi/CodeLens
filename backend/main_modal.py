import os
import modal
from main import app
from review_engines.base import BaseReviewEngine
from core.logging_config import logger

HF_CACHE_MOUNT_PATH = "/data/hf_cache"
DB_MOUNT_PATH = "/data/db"
DB_FILE_PATH = os.path.join(DB_MOUNT_PATH, "review.db")

BASE_MODEL_NAME = os.environ.get("BASE_MODEL_NAME", "refactai/Refact-1_6B-fim")
USE_GPU = os.environ.get("USE_GPU", "1") == "1"

app = modal.App("codelens-backend")

hf_vol = modal.Volume.from_name("codelens-hf-cache", create_if_missing=True)
db_vol = modal.Volume.from_name("codelens-sqlite-db", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "libsm6", "libxext6", "build-essential")
    .pip_install_from_requirements("requirements.txt")
    .pip_install(
        "torch==1.13.1+cu117",
        "torchvision==0.14.1+cu117",
        "torchaudio==0.13.1+cu117",
        index_url="https://download.pytorch.org/whl/cu117",
    )
)

def _prepare_env():
    os.environ.setdefault("HF_HOME", HF_CACHE_MOUNT_PATH)
    os.environ.setdefault("TRANSFORMERS_CACHE", HF_CACHE_MOUNT_PATH)
    os.environ.setdefault("DB_PATH", DB_FILE_PATH)
    if "HUGGINGFACE_TOKEN" not in os.environ:
        logger.warning("HUGGINGFACE_TOKEN not found. Private models may fail to load.")

@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT_PATH: hf_vol, DB_MOUNT_PATH: db_vol})
def preload_model():
    """Runs once per container to warm up model & cache"""
    _prepare_env()
    os.makedirs(HF_CACHE_MOUNT_PATH, exist_ok=True)
    os.makedirs(DB_MOUNT_PATH, exist_ok=True)
    BaseReviewEngine.preload_model(
        model_name=BASE_MODEL_NAME,
        device=0 if USE_GPU else -1,
        hf_token=os.environ.get("HUGGINGFACE_TOKEN"),
    )
    logger.info("✅ Preload complete for model: %s", BASE_MODEL_NAME)

@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT_PATH: hf_vol, DB_MOUNT_PATH: db_vol})
@modal.asgi_app()
def fastapi_app():
    """Main FastAPI ASGI entrypoint"""
    _prepare_env()
    try:
        preload_model.remote()
    except Exception as e:
        logger.exception("Preload trigger failed: %s", e)
    return app