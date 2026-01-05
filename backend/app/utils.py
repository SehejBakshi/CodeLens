import os
import tempfile
import zipfile
import shutil
from typing import List
from git import Repo

def extract_zip(zip_path: str) -> str:
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def clone_git_repo(git_url: str, clone_to: str = None) -> str:
    target_dir = clone_to or tempfile.mkdtemp()
    Repo.clone_from(git_url, target_dir)
    return target_dir

def enumerate_source_files(path: str, extensions: List[str] = None) -> List[str]:
    extensions = extensions or ["py"]
    files = []
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        if ext in extensions:
            files.append(path)
    else:
        for root, _, filenames in os.walk(path):
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lstrip('.').lower()
                if ext in extensions:
                    files.append(os.path.join(root, fname))
    return files

def cleanup_path(path: str):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
