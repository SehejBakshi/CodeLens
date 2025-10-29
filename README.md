# 🧠 CodeLens — AI-Powered Code Review Platform

CodeLens is a modular, full-stack code review platform designed for analyzing and reviewing source code from multiple sources — including direct input, file uploads, and GitHub repositories. It uses asynchronous job handling for scalable performance, supports GPU acceleration, and is designed for easy future extension.

---

## 🚀 Features

### 🔧 Core Functionality
- Review **raw source code**, **uploaded files**, or **entire GitHub repositories**
- Asynchronous job queue with background task processing (`asyncio`)
- Real-time job tracking via job IDs
- Unified job creation and management
- Persistent job storage via database (`SQLite3`)
- Get **Code reviews**, **Architecture Feedback with diagrams** and **Security findings**

### 💻 Frontend (Next.js + TailwindCSS)
- Modern, minimal, responsive design using TailwindCSS
- Code editor built with Monaco Editor (`@monaco-editor/react`)
- Dynamic code input card with styled slider and animated transitions
- Snackbar notifications for job success / error states
- Enhanced buttons and inputs across pages (`CodeInput`, `FileUpload`, `GithubRepoInput`)
- Modular component design for reuse and scalability

### ⚙️ Backend (FastAPI + Python)
- Modular async architecture
- Unified job creation logic
- File, code, and GitHub URL analysis handled independently
- Built-in GPU support for ML-based review models (PyTorch)
- Centralized error handling and structured logging
- Integrated health checks and background workers

---

## 🧩 Directory Structure

```bash
CodeLens/
│
└── backend/
| └── core/
| | └── logging_config.py
| └── models/
| | └── job_status.py
│ └── review_engines/
│ │ └── base.py
│ │ └── python_engine.py
│ └── test_scripts/
│ │ └── test_script1.py
│ │ └── test_script2.py
│ └── analyzer.py
│ └── db.py
│ └── main.py
│ └── old_analyzer.py
│ └── personalization.py
│ └── prepare_files.py
│ └── requirements.txt
│ └── schemas.py
│ └── security.py
│ └── utils.py
│
├── frontend/
│ └── app/
│ │ └── page.tsx
│ │ └── layout.tsx
│ │ └── layout.css
│ │ └── page.tsx
│ │ └── components/
│ │ │ └── ArchitectureDiagram.tsx
│ │ │ └── CodeInput.tsx
│ │ │ └── FileUpload.tsx
│ │ │ └── GithubRepoInput.tsx
│ │ │ └── JobStatusLoader.tsx
│ │ │ └── ReviewResult.tsx
│ │ │ └── StatusBadge.tsx
| └── lib/
│ │ └── api.ts
│ └── styles/
│ │ └── globals.css
└── utils/
│ │ └── StarterCodes.ts
│
└── .gitignore
└── CODEOWNERS
└── docker-compose.yml
└── Dockerfile.backend
└── Dockerfile.frontend
└── LICENSE
└── README.md
```

---

## ⚡ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Next.js 15, React, TailwindCSS, Monaco Editor |
| **Backend** | FastAPI, Python 3.10+, asyncio |
| **AI/ML** | PyTorch (GPU-accelerated) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Logging** | Python `logging` module (configurable for Elastic/Kibana) |
| **Job Management** | Custom async queue with in-memory + DB persistence |

---

## 🔁 Async Job Workflow

1. A new request (code, file, or repo) triggers `schedule_job()`.
2. A unique `job_id` is created and stored in both memory and DB.
3. A background task (`asyncio.create_task(process_job())`) begins processing.
4. The frontend polls or queries `/status/{job_id}` to fetch updates.
5. Once completed, results or errors are updated in DB and memory.
6. Snackbar notifications inform the user on the frontend.

---
## 🧠 GPU Support

The backend supports GPU acceleration using PyTorch.

If you encounter CUDA issues, reload the UVM kernel modules:

``` bash
sudo rmmod nvidia_uvm
sudo modprobe nvidia_uvm
```

Verify GPU availability:
``` python
import torch
print(torch.cuda.is_available())  # should return True
```

## 🧪 Local Development

### Frontend

``` bash
cd frontend
nvm use <version> # in case of multiple node versions
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv # To create virtual environment 
source venv/bin/activate
pip install -r requirements.txt
```

#### PyTorch Installation (Environment specific)

PyTorch packages are excluded from `requirements.txt` to avoid build and deployment conflicts.

##### For GPU environments:
```bash
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1+cu117 --index-url https://download.pytorcg.org/whl/cu117
```

##### For CPU environments
```bash
pip install torch==1.13.1+cpu torchvision==0.14.1+cpu torchaudio==0.13.1+cpu --index-url https://download.pytorcg.org/whl/cpu
```

Then, to run:
```bash
uvicorn main:app --reload
```

### Next (possible) steps
- Multi-language static analysis engines
- Job queue persistence with Redis or RabbitMQ
- Authentication and user accounts
- Role-based dashboards for reviewers
- Live job progress via WebSockets
