import os
from typing import List
from schemas import ReviewRequest, FileReview
from utils import clone_git_repo, enumerate_source_files, extract_zip

def prepare_files(input: ReviewRequest) -> List[FileReview]:
    files: List[FileReview] = []

    # Raw code
    if input.code:
        files.append(FileReview(code=input.code, filename=input.filename or "<stdin>"))
        return files

    # Local file
    if input.filename and os.path.exists(input.filename):
        with open(input.filename, 'r', encoding='utf-8') as f:
            code = f.read()
        files.append(FileReview(code=code, filename=input.filename))
        return files

    # Uploaded file or zip
    if input.uploaded_file_path and os.path.exists(input.uploaded_file_path):
        ext = os.path.splitext(input.uploaded_file_path)[1].lower()
        if ext == ".zip":
            temp_dir = extract_zip(input.uploaded_file_path)
            paths = enumerate_source_files(temp_dir, extensions=["py"])
            for p in paths:
                with open(p, 'r', encoding='utf-8') as f:
                    files.append(FileReview(code=f.read(), filename=p))
        else:
            with open(input.uploaded_file_path, 'r', encoding='utf-8') as f:
                files.append(FileReview(code=f.read(), filename=input.uploaded_file_path))
        return files

    # GitHub repo
    if input.git_url:
        temp_dir = clone_git_repo(input.git_url, clone_to=None)
        paths = enumerate_source_files(temp_dir, extensions=["py"])
        for p in paths:
            with open(p, 'r', encoding='utf-8') as f:
                files.append(FileReview(code=f.read(), filename=p))
        return files

    return files