# 🏍️ Bikes TextToSQL Agent

A powerful natural language to SQL conversion agent specialized for motorcycle/bike data analysis, built with OpenAI API, PostgreSQL, and Streamlit.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python database_setup.py

# Run the application
streamlit run app.py
```

## 📁 Project Structure

```
TextToSQLAgent/
├── src/                          # Source code
│   ├── config/                   # Configuration management
│   ├── core/                     # Core TextToSQL agent logic
│   └── utils/                    # Utility functions
├── tests/                        # Test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── performance/              # Performance tests
├── docs/                         # Documentation
│   ├── user_guide/               # User guides and setup
│   ├── api/                      # API documentation
│   └── development/              # Development documentation
├── version_history/              # Version change logs
├── data/                         # Data files
├── logs/                         # Application logs
└── config/                       # Configuration files
```



Copy `env.example` to `.env` and configure your environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bikes_database
DB_USER=postgres
DB_PASSWORD=your_database_password_here
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests
python -m pytest tests/
```

## 📈 Features

- **Natural Language to SQL**: Convert bike-related questions to SQL queries
- **Data Analysis**: Generate insights and visualizations from query results
- **Multi-Brand Support**: Query bikes from various manufacturers
- **Performance Metrics**: Analyze speed, power, mileage, and pricing
- **Interactive UI**: User-friendly Streamlit interface



This project is licensed under the MIT License.

## 🔗 Links

- [Version History](version_history/) - Track project changes and updates
- [Issue Tracker](https://github.com/your-repo/issues) - Report bugs and feature requests 
