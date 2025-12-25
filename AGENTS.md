## Tooling for Shell Interactions

Is it about finding FILES? use 'fd'
Is it about finding TEXT/STRINGS/CODE STRUCTURE? use 'ast-grep'
Is it about SELECTING from multiple results? pipe to 'fzf'
Is it about interacting with JSON? use 'jq'
Is it about interacting with YAML or XML? use 'yq'

Note on searches:

- This environment has `ast-grep` available. Example: `ast-grep --lang python -p '<pattern>'` (set `--lang` appropriately for the language you are querying).
- Prefer syntax-aware or structural matching with `ast-grep` by default. Do not fall back to plain-text tools like `rg` or `grep` unless explicitly requested, or when they are clearly the better tool for the job.

---

## Project Structure

```
noma/
├── src/noma/                    # Python backend package
│   ├── api/                     # Flask API module
│   │   ├── __init__.py          # Exports create_app
│   │   ├── app.py               # Flask application factory
│   │   ├── routes.py            # API route definitions
│   │   └── streaming.py         # Video streaming with GraphRAG
│   ├── rag/                     # RAG module
│   │   ├── __init__.py          # Exports graph/ehr/viz functions
│   │   ├── graphrag.py          # Neo4j GraphRAG integration
│   │   ├── ehr.py               # EHR Q&A with LangChain
│   │   └── visualization.py     # Graph visualization with pyvis
│   ├── transcription/           # Transcription module
│   │   ├── __init__.py          # Exports transcribe_video
│   │   └── aws.py               # AWS Transcribe integration
│   ├── __init__.py              # Package exports
│   ├── __main__.py              # CLI entry point
│   └── config.py                # Configuration management
├── frontend/
│   ├── mesh-viewer/             # React Three.js point cloud app
│   │   ├── src/                 # React source files
│   │   │   ├── App.js           # Main application
│   │   │   ├── PointCloud.js    # Point cloud component
│   │   │   └── index.js         # Entry point
│   │   └── public/              # Static assets
│   └── incision-tool/           # Static Three.js incision demo
│       ├── index.html           # Main application
│       └── models/              # 3D face model assets
├── presentation/                # Streamlit demo dashboard
├── templates/                   # Flask Jinja2 templates
├── transcripts/                 # Generated transcript JSON files
├── assets/                      # Demo screenshots
├── data/
│   ├── mohs/                    # GraphRAG knowledge base cache
│   └── patient.pdf              # Sample EHR document
└── media/
    └── mohs.mp4                 # Sample surgery video
```

---

## Architecture

### Backend (Python)

The backend uses a deep modular package structure under `src/noma/`:

#### API Module (`noma.api`)
- **app.py**: Flask application factory with CORS support
- **routes.py**: API endpoint definitions (video feed, text feed, status)
- **streaming.py**: Video streaming class with GraphRAG analysis at intervals

#### RAG Module (`noma.rag`)
- **graphrag.py**: Wraps nano-graphrag with Neo4j storage, Ollama queries
- **ehr.py**: Gradio app for RAG-based Q&A against patient PDF records
- **visualization.py**: Exports Neo4j knowledge graphs to interactive HTML

#### Transcription Module (`noma.transcription`)
- **aws.py**: Segments video audio and transcribes via AWS Transcribe

#### Configuration (`noma.config`)
- Dataclass-based configuration loaded from environment variables
- Supports Neo4j, AWS, and OpenAI settings

All modules load credentials from environment variables (see `.env.example`).

### Frontend (JavaScript)

Two separate frontend applications:

1. **mesh-viewer**: React app using Three.js and @react-three/fiber for 2D-to-3D point cloud visualization with surgical annotations
2. **incision-tool**: Static HTML/JS demo using Three.js for incision simulation on a 3D face model

### Client-Server Communication

```
┌─────────────────┐     HTTP/SSE      ┌─────────────────┐
│  mesh-viewer    │◄────────────────►│  Flask API      │
│  (React)        │   /video_feed    │  (noma.api)     │
└─────────────────┘   /text_feed     └─────────────────┘
                      /api/status            │
                                             ▼
                                    ┌─────────────────┐
                                    │  Neo4j + RAG    │
                                    └─────────────────┘
```

---

## Development

```bash
# Install Python dependencies
uv sync

# Run Flask API
uv run noma
# or
uv run python -m noma

# Run EHR Q&A
uv run noma-ehr

# Frontend (mesh-viewer)
cd frontend/mesh-viewer && npm install && npm start

# Frontend (incision-tool)
# Open frontend/incision-tool/index.html in browser

# Run linting
uv run ruff check src/

# Run tests
uv run pytest
```

---

## Key Dependencies

- **nano-graphrag**: Lightweight GraphRAG implementation
- **neo4j**: Graph database driver
- **langchain**: RAG chain construction
- **gradio**: EHR Q&A web interface
- **flask**: Python web framework with CORS support
- **three.js**: 3D visualization (frontend)
