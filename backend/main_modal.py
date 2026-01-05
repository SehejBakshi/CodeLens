import os
import modal

app = modal.App("codelens-backend")

HF_CACHE_MOUNT_PATH = "/data/hf_cache"
DB_MOUNT_PATH = "/data/db"
DB_FILE_PATH = os.path.join(DB_MOUNT_PATH, "review.db")

USE_GPU = os.environ.get("USE_GPU", "1") == "1"

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
    .run_commands(
        "git clone https://github.com/SehejBakshi/CodeLens.git /app"
    )
    .env({"PYTHONPATH": "/app/backend"})
)

@app.function(image=image, gpu="A10G", secrets=[modal.Secret.from_name("codelens-secrets")], volumes={HF_CACHE_MOUNT_PATH: hf_vol, DB_MOUNT_PATH: db_vol})
@modal.enter()
def startup():
    from app.config import load_llm_config
    from app.review_engines.base import BaseReviewEngine

    config = load_llm_config(require_explicit=True)
    BaseReviewEngine.initialize_global(config)

@app.function(image=image, gpu="A10G", secrets=[modal.Secret.from_name("codelens-secrets")], volumes={HF_CACHE_MOUNT_PATH: hf_vol, DB_MOUNT_PATH: db_vol})
@modal.asgi_app()
def fastapi_app():
    from app.main import app as fastapi_app_instance
    from app.core.logging_config import logger
    
    return fastapi_app_instance