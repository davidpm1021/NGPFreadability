# NGPF Readability Analyzer

Internal tool to analyze readability metrics for articles linked in NGPF curriculum. Processes bulk URLs to extract text and calculate multiple readability scores (Flesch-Kincaid, SMOG, Coleman-Liau, ARI) for baseline comparison with future simplified versions.

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- Trafilatura (text extraction)
- textstat (readability metrics)
- aiohttp (async URL fetching)

**Frontend:**
- React 19
- TypeScript
- Vite
- Tailwind CSS
- Axios

## Quick Start

### Prerequisites
- Python 3.11 or higher ([Download](https://www.python.org/downloads/))
- Node.js 18 or higher ✅
- npm or yarn ✅

**Note:** Python is not currently installed on this system. Install Python 3.11+ before proceeding with backend setup.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

### Code Quality

**Backend:**
```bash
# Format code
black app/

# Lint code
ruff check app/

# Type checking
mypy app/
```

**Frontend:**
```bash
# Lint code
npm run lint

# Run tests with coverage
npm run test:coverage
```

## Project Structure

```
NGPFreadability/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── models/       # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── tests/        # Test suite
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API integration
│   │   ├── types/        # TypeScript types
│   │   ├── utils/        # Utility functions
│   │   └── tests/        # Test suite
│   ├── package.json
│   └── vitest.config.ts
│
├── CLAUDE.md            # Technical documentation
├── PRD.md               # Product requirements
└── SPRINTS.md           # Sprint plan
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `GET /health` - Health check
- `POST /api/analyze-urls` - Analyze readability of multiple URLs

## Environment Variables

**Backend** (create `.env` from `.env.example`):
```
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
EXTRACTION_TIMEOUT=10
MAX_CONCURRENT_REQUESTS=10
```

**Frontend** (create `.env` from `.env.example`):
```
VITE_API_BASE_URL=http://localhost:8000
```

## Testing Strategy

- Test-Driven Development (TDD) approach
- Minimum 80% code coverage requirement
- Unit tests for all utilities and services
- Integration tests for API endpoints
- Component tests with React Testing Library

## Current Status

**Sprint 0: Foundation & Setup** - ✅ Complete

See [SPRINTS.md](./SPRINTS.md) for detailed sprint plan and progress.

## Contributing

1. Follow TDD approach - write tests before implementation
2. Maintain 80% test coverage
3. Use type hints in Python code
4. Use TypeScript (no `any` types)
5. Format code before committing

## License

Internal tool for NGPF use only.
