# 🤖 Multi-Domain Text-to-SQL Agent

A sophisticated natural language to SQL conversion system that supports multiple databases, powered by Azure OpenAI GPT-4.1 and PostgreSQL. Now featuring **Airlines** and **Bikes** databases with intelligent context switching.

## 🎯 Features

### 🔥 **Multi-Database Support**
- **✈️ Airlines Database**: Flight information, routes, prices, schedules, and airline data
- **🏍️ Bikes Database**: Motorcycle specifications, performance, features, and pricing
- **🔄 Dynamic Context Switching**: Seamlessly switch between databases with a dropdown selector
- **🧠 Context-Aware Processing**: Each database has specialized prompts and validation

### 🚀 **Core Capabilities**
- **Natural Language Processing**: Convert plain English questions to SQL queries
- **Intelligent Query Generation**: Context-aware SQL generation for each database domain
- **Real-time Data Analysis**: Get instant insights and patterns from your data
- **Interactive Visualizations**: Auto-generated charts and graphs using Plotly
- **Error Handling**: Robust error management with helpful suggestions
- **Query History**: Track and revisit previous queries
- **Export Functionality**: Download results as CSV files

### 🛡️ **Security & Architecture**
- **Environment-based Configuration**: All sensitive data in `.env` files
- **Context Restriction**: Prevents out-of-scope questions for each database
- **Modular Design**: Clean, maintainable codebase with proper separation of concerns
- **Professional Structure**: Production-ready architecture

## 🏗️ Project Structure

```
TextToSQLAgent/
├── src/                          # Source code
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Environment-based settings
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   └── text_to_sql_agent.py # Main agent class with multi-DB support
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── database.py          # Multi-database operations
│   │   └── visualization.py     # Chart generation
│   └── __init__.py
├── data/                         # Data files
│   ├── airlines_flights_data.csv # Airlines dataset
│   └── bike_information.csv     # Bikes dataset
├── docs/                         # Documentation
├── tests/                        # Test files
├── app.py                       # Main Streamlit application with DB selector
├── database_setup.py            # Multi-database setup script
├── test_multi_database.py       # Comprehensive test suite
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
├── .gitignore                   # Git ignore file
└── README.md                    # This file
```

## 🗃️ Database Schemas

### ✈️ Airlines Database
```sql
-- Airlines table: airline_id, airline_name, airline_code
-- Cities table: city_id, city_name, country
-- Flights table: flight_id, airline_id, source_city_id, destination_city_id,
--                flight_number, departure_time, arrival_time, stops, 
--                class_type, duration, days_left, price
```

**Sample Airlines Queries:**
- "Show me flights from Delhi to Mumbai"
- "Find the cheapest flights under 5000 rupees"
- "Which airlines fly to Bangalore?"
- "What are the average prices by airline?"

### 🏍️ Bikes Database
```sql
-- Bike_brands table: brand_id, brand_name
-- Bikes table: bike_id, bike_name, brand_id, engine_capacity, transmission,
--              colors, price, max_power, max_torque, top_speed, cylinders,
--              fuel_type, mileage, fuel_tank_capacity, kerb_weight, abs_available
```

**Sample Bikes Queries:**
- "Show me all Ducati bikes"
- "Find bikes under 10 lakhs"
- "Which bikes have ABS?"
- "Show me bikes with mileage above 15 km/l"

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Azure OpenAI Service access

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/HemanthVarmaKonduru/TextToSQLAgent.git
cd TextToSQLAgent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your credentials
```

5. **Setup databases:**
```bash
python database_setup.py
```

6. **Run the application:**
```bash
streamlit run app.py
```

## ⚙️ Environment Configuration

Create a `.env` file with your configuration:

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
STREAMLIT_TITLE=Multi-Domain Text-to-SQL Agent
STREAMLIT_DESCRIPTION=Convert natural language to SQL queries for multiple databases
```

## 🎮 How to Use

### 1. **Select Database**
- Choose between **Airlines** or **Bikes** database from the dropdown
- Each database has its own specialized context and sample queries

### 2. **Ask Questions**
- Type your question in natural language
- Use the sample queries as examples
- Be specific about what you want to know

### 3. **View Results**
- See the generated SQL query
- Analyze the data in an interactive table
- Read AI-generated insights
- Explore auto-generated visualizations

### 4. **Export Data**
- Download results as CSV files
- Save visualizations as images
- Track query history in the sidebar

## 📊 Example Queries

### Airlines Database Examples:
```sql
-- "Show me flights from Delhi to Mumbai"
SELECT f.flight_id, a.airline_name, f.flight_number, 
       sc.city_name AS source_city, dc.city_name AS destination_city, 
       f.departure_time, f.arrival_time, f.price
FROM flights f
JOIN airlines a ON f.airline_id = a.airline_id
JOIN cities sc ON f.source_city_id = sc.city_id
JOIN cities dc ON f.destination_city_id = dc.city_id
WHERE LOWER(sc.city_name) = 'delhi' AND LOWER(dc.city_name) = 'mumbai'
ORDER BY f.departure_time LIMIT 100;
```

### Bikes Database Examples:
```sql
-- "Show me all Ducati bikes"
SELECT b.bike_name, b.engine_capacity, b.max_power, b.price, b.top_speed
FROM bikes b
JOIN bike_brands br ON b.brand_id = br.brand_id
WHERE LOWER(br.brand_name) = 'ducati'
ORDER BY b.bike_name LIMIT 100;
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_multi_database.py
```

This tests:
- ✅ Airlines database queries
- ✅ Bikes database queries  
- ✅ Context restriction (prevents off-topic questions)
- ✅ Database switching functionality
- ✅ Statistical analysis
- ✅ Error handling

## 🔧 Development

### Adding New Databases

1. **Update Database Setup** (`database_setup.py`):
   - Add new table creation functions
   - Add data insertion functions
   - Update schema information

2. **Update Database Manager** (`src/utils/database.py`):
   - Add new schema method
   - Update quick stats function
   - Add sample queries

3. **Update Agent** (`src/core/text_to_sql_agent.py`):
   - Add new system prompt method
   - Update context validation
   - Add domain-specific processing

4. **Update UI** (`app.py`):
   - Add database option to dropdown
   - Update help text and examples
   - Add domain-specific visualizations

### Code Quality
- Type hints throughout the codebase
- Comprehensive logging
- Modular architecture
- Extensive test coverage
- Professional documentation

## 🛡️ Security Features

- **API Key Protection**: All sensitive data in environment variables
- **Context Validation**: Prevents queries outside database scope
- **Input Sanitization**: SQL injection protection
- **Error Handling**: Graceful failure management
- **Access Control**: Database-level permissions

## 📈 Performance

- **Optimized Queries**: Efficient SQL generation with LIMIT clauses
- **Connection Pooling**: Proper database connection management
- **Caching**: Streamlit session state for agent instances
- **Parallel Processing**: Multi-database support without conflicts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Azure OpenAI** for powerful language model capabilities
- **Streamlit** for the intuitive web interface
- **PostgreSQL** for robust database management
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation

---

## 📞 Support

For issues, questions, or contributions:
- 📧 Email: [your-email@example.com]
- 💬 GitHub Issues: [Create an issue](https://github.com/HemanthVarmaKonduru/TextToSQLAgent/issues)
- 📖 Documentation: Check the `/docs` folder for detailed guides

**🎉 Ready to explore your data with natural language? Start asking questions!** 