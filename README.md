# ✈️ Airlines Text-to-SQL Agent

A sophisticated natural language to SQL conversion system for airlines data analysis, powered by Azure OpenAI GPT-4.1 and PostgreSQL.

## 🎯 Features

- **Natural Language to SQL**: Convert human queries to PostgreSQL queries
- **Context-Aware**: Only processes airlines-related questions
- **AI-Powered Insights**: Generate meaningful insights from query results
- **Interactive Visualizations**: Automatic chart generation with Plotly
- **Secure Configuration**: Environment-based configuration management
- **Professional UI**: Beautiful Streamlit interface with error handling

## 🏗️ Project Structure

```
TextToSQLAgent/
├── src/                          # Source code
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Environment-based settings
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   └── text_to_sql_agent.py # Main agent class
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── database.py          # Database operations
│   │   └── visualization.py     # Chart generation
│   └── __init__.py
├── data/                         # Data files
│   └── airlines_flights_data.csv
├── docs/                         # Documentation
├── tests/                        # Test files
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- Azure OpenAI account with GPT-4.1 deployment

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd TextToSQLAgent

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env file with your credentials
nano .env
```

### 3. Environment Configuration

Create a `.env` file with the following variables:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airlines_db
DB_USER=postgres
DB_PASSWORD=your_database_password_here

# Application Configuration
STREAMLIT_TITLE=Airlines Text-to-SQL Agent
STREAMLIT_DESCRIPTION=Convert natural language to SQL queries for airlines data and get insights
```

### 4. Database Setup

```bash
# Run database setup script
python database_setup.py

# Test database connection
python test_db_connection.py
```

### 5. Run the Application

```bash
# Start the main application
streamlit run app.py
```

## 📊 Database Schema

### Airlines Table
- `airline_id` (SERIAL PRIMARY KEY)
- `airline_name` (VARCHAR(100) NOT NULL UNIQUE)
- `airline_code` (VARCHAR(10))

### Cities Table
- `city_id` (SERIAL PRIMARY KEY)
- `city_name` (VARCHAR(100) NOT NULL UNIQUE)
- `country` (VARCHAR(50) DEFAULT 'India')

### Flights Table
- `flight_id` (SERIAL PRIMARY KEY)
- `airline_id` (INTEGER REFERENCES airlines(airline_id))
- `flight_number` (VARCHAR(20))
- `source_city_id` (INTEGER REFERENCES cities(city_id))
- `destination_city_id` (INTEGER REFERENCES cities(city_id))
- `departure_time` (VARCHAR(20))
- `arrival_time` (VARCHAR(20))
- `stops` (VARCHAR(20))
- `class_type` (VARCHAR(20))
- `duration` (DECIMAL(5,2))
- `days_left` (INTEGER)
- `price` (INTEGER)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

## 💡 Example Queries

### Valid Airlines Questions ✅
- "Show me flights from Delhi to Mumbai"
- "Find the cheapest flights under 5000 rupees"
- "Which airlines fly to Bangalore?"
- "Show me business class flights"
- "Find flights with no stops"
- "What are the average prices by airline?"
- "Show me flights departing in the morning"
- "Which routes have the highest prices?"

### Invalid Questions ❌
- "Who is the president of India?"
- "What is the weather like?"
- "How to cook pasta?"
- "What is 2+2?"

## 🔧 Development

### Project Structure Benefits

1. **Modular Design**: Clean separation of concerns
2. **Configuration Management**: Secure environment-based settings
3. **Type Hints**: Full type annotations for better IDE support
4. **Error Handling**: Comprehensive error handling and logging
5. **Documentation**: Detailed docstrings and comments

### Adding New Features

1. **New Database Operations**: Add to `src/utils/database.py`
2. **New Visualizations**: Add to `src/utils/visualization.py`
3. **Configuration Changes**: Update `src/config/settings.py`
4. **Core Logic**: Modify `src/core/text_to_sql_agent.py`

### Testing

```bash
# Run tests
python -m pytest tests/

# Test specific functionality
python test_airlines_queries.py
```

## 🛡️ Security Features

- **Environment Variables**: All sensitive data stored in `.env`
- **Input Validation**: Comprehensive query validation
- **Context Restrictions**: Only airlines-related queries allowed
- **Error Handling**: Secure error messages without data exposure
- **Database Security**: Proper connection management

## 📈 Performance

- **Caching**: Efficient database connection pooling
- **Optimization**: Query optimization and result limiting
- **Memory Management**: Proper DataFrame handling
- **Async Support**: Ready for async operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for all classes and methods
- Write tests for new functionality
- Update documentation for any changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Azure OpenAI for providing the GPT-4.1 model
- Streamlit for the web framework
- Plotly for interactive visualizations
- PostgreSQL for the database system

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the troubleshooting guide

---

**Made with ❤️ for Airlines Data Analysis** 