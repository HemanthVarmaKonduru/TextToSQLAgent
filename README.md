# Multi-Domain Text-to-SQL Agent

A natural language to SQL conversion platform that lets users query databases using plain English. Built with OpenAI GPT-4o, PostgreSQL, Supabase Auth, and Streamlit.

Supports **multiple domains** — currently Airlines and Bikes databases — with automatic schema detection, AI-powered insights, and interactive visualizations.

## Features

- **Natural Language Queries** — Ask questions in plain English, get SQL + results
- **Multi-Database Support** — Switch between Airlines and Bikes datasets
- **AI-Powered Insights** — GPT-4o analyzes query results and provides business insights
- **Interactive Visualizations** — Auto-generated Plotly charts based on result data
- **SQL Editor** — View, edit, and re-run generated SQL queries
- **User Authentication** — Supabase Auth with email/password and Google OAuth
- **Query History** — Track past queries within a session
- **CSV Export** — Download query results as CSV files
- **Sample Queries** — Pre-built queries organized by difficulty (basic, intermediate, advanced)

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Streamlit  │────>│  Text-to-SQL     │────>│  PostgreSQL  │
│   Frontend   │     │  Agent (GPT-4o)  │     │  Database    │
│              │<────│                  │<────│              │
└──────────────┘     └──────────────────┘     └──────────────┘
       │                                             │
       │              ┌──────────────┐               │
       └─────────────>│  Supabase    │               │
                      │  Auth        │               │
                      └──────────────┘               │
                      ┌──────────────┐               │
                      │  Plotly       │<──────────────┘
                      │  Viz Engine   │
                      └──────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| LLM | OpenAI GPT-4o-mini |
| Database | PostgreSQL |
| Auth | Supabase |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy |
| Language | Python 3.8+ |

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL server
- OpenAI API key
- Supabase project (for auth)

### Setup

```bash
# Clone
git clone https://github.com/HemanthVarmaKonduru/TextToSQLAgent.git
cd TextToSQLAgent

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Environment
cp env.example .env
# Edit .env with your credentials
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `OPENAI_MODEL` | No | Model name (default: `gpt-4o-mini`) |
| `DB_HOST` | Yes | PostgreSQL host |
| `DB_PORT` | No | PostgreSQL port (default: `5432`) |
| `DB_NAME` | Yes | Database name |
| `DB_USER` | Yes | Database username |
| `DB_PASSWORD` | Yes | Database password |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | Supabase anonymous key |
| `OAUTH_REDIRECT_URL` | No | OAuth redirect URL (default: `http://localhost:8501`) |

### Run

```bash
# Set up database tables
python database_setup.py

# Launch the app
streamlit run app.py
```

## Project Structure

```
TextToSQLAgent/
├── app.py                     # Main Streamlit application
├── login.py                   # Authentication page
├── database_connection.py     # Database connection page
├── auth_service.py            # Supabase auth wrapper
├── database_setup.py          # Database initialization
├── src/
│   ├── config/settings.py     # Centralized configuration
│   ├── core/text_to_sql_agent.py  # NLP-to-SQL conversion engine
│   └── utils/
│       ├── database.py        # Database operations & query execution
│       └── visualization.py   # Plotly chart generation
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Documentation
├── data/                      # Sample data files
├── requirements.txt
├── env.example
└── LICENSE
```

## Testing

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v
```

## License

MIT License — see [LICENSE](LICENSE) for details.
