# 🚀 Quick Setup Guide

## Option 1: Demo Mode (No Database Required)

The demo application is already running and shows the Text-to-SQL conversion capabilities:

```bash
streamlit run demo_app.py
```

This will open at `http://localhost:8501` and allows you to:
- ✅ Test natural language to SQL conversion
- ✅ See generated SQL queries
- ✅ View demo visualizations
- ✅ Experience the UI without database setup

## Option 2: Full Setup with PostgreSQL

### Step 1: Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Step 2: Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE texttosql_db;

# Create user (optional)
CREATE USER texttosql_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE texttosql_db TO texttosql_user;

# Exit
\q
```

### Step 3: Configure Environment

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=texttosql_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### Step 4: Set Up Sample Data

```bash
python database_setup.py
```

### Step 5: Run Full Application

```bash
streamlit run streamlit_app.py
```

## 🔧 Troubleshooting

### Database Connection Issues

1. **Check if PostgreSQL is running:**
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   ```

2. **Test connection:**
   ```bash
   psql -h localhost -U postgres -d texttosql_db
   ```

3. **Common fixes:**
   - Update password in `.env` file
   - Check if port 5432 is available
   - Ensure database exists

### Azure OpenAI Issues

1. **Check API key and endpoint in `config.py`**
2. **Verify deployment name exists**
3. **Ensure sufficient API quota**

### Import Errors

```bash
pip install -r requirements.txt
```

## 📊 What You Get

### Demo Mode:
- Natural language to SQL conversion
- Sample visualizations
- Beautiful UI experience

### Full Mode:
- ✅ Complete database integration
- ✅ Real data execution
- ✅ AI-powered insights
- ✅ Interactive visualizations
- ✅ Data export capabilities
- ✅ Schema-aware queries

## 🎯 Example Queries to Try

1. "Show me total sales by product category"
2. "Find the top 5 customers by total purchase amount"
3. "What is the average salary by department?"
4. "Show sales trend over the last 3 months"
5. "Which products have the highest stock quantity?"

## 🚀 Next Steps

1. **Start with demo mode** to see the capabilities
2. **Set up PostgreSQL** for full functionality
3. **Customize the schema** for your own data
4. **Deploy to production** using Streamlit Cloud or similar

---

**Happy Querying! 🎉** 