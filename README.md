# Personal Bookmarks Manager RESTful API

A structured, layered backend service engineered with FastAPI and SQLite designed to safely catalog, tag, search, and manage web assets across isolated user boundaries.

## Architecture Highlights
- **Layered Design**: Clean separation between routing entrypoints (`app/api`), service transaction engines (`app/services`), data persistence validation (`app/schemas`), and ORM records (`app/models`).
- **Raw SQL Execution**: High-performance data compilation using direct database aggregates (`GROUP BY`, date formatting, and analytical joins) to optimize metric calculations without ORM overhead.

####
# Instructions
####

# a. Installing pip. This is (optional) - (I had to do it to fix my existing environment).
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade sqlalchemy
delete all .pytest_cache, _pycache_ folders, if the code is modified after execution and test is runned    

# 1. Install dependencies
pip install -r requirements.txt

# 2. Testing
python -m pytest -v or pytest -v

# 3. Launch Application Engine with Swagger UI
python run.py --> this will start the server on http://localhost:9500/api/docs

# ############ Seed Optional ########################
# 4. Seed the database 
python seed.py
# 5. Testing Seeded database 
python -m pytest tests/test_seed.py -v
# 6. Clear Seeded data 
python clear_seed.py
# ############ Seed Optional Ends ########################

# ############ DOCKER Optional ########################
# This is un-verified

# 7. Docker Setup
docker build --target test-runner -t bookmarks-test-suite .
# 8. Up the Environment Locally
docker compose up --build -d
# 9. URL to test swagger UI
http://localhost:9500/api/docs
# 10. Check logs
docker compose logs -f
# 11. Teardown the Environment Locally
docker compose down

# ############ DOCKER Optional Ends ########################
