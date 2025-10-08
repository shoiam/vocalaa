<p align="center">
  <img src="assets/VocalaaLogoGithub.jpg" alt="Vocalaa Logo" width="300"/>
</p>

# Vocalaa - Interactive Professional Profiles

Transform your resume into an interactive MCP server that people can query conversationally.

## Architecture
- **Backend**: FastAPI + Supabase + Redis
- **Frontend**: Next.js + Supabase Auth
- **Deployment**: Railway

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Supabase account
- Redis instance

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r pyproject.toml
cp .env.example .env
# Edit .env with your configuration
python -m app.main
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd ui
npm install
cp .env.example .env
# Edit .env with your Supabase configuration
npm run dev
```

Frontend will be available at http://localhost:3000

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project.

## Project Structure

```
vocalaa/
├── backend/          # FastAPI backend application
│   ├── app/         # Application code
│   └── tests/       # Backend tests
├── ui/              # Next.js frontend application
│   └── src/         # Frontend source code
└── CONTRIBUTING.md  # Contribution guidelines
```

## License

[Your License Here]
