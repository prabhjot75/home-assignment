# Refer to docs folder for more information on the requirements

# Architecture - 
#    Seperation of concern principle is followed, for a modular, domain-agnostic layered architecture

####
# Instructions
####

# a. Installing pip. This is (optional) - (I had to do it to fix my existing environment).
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade sqlalchemy
delete all .pytest_cache, _pycache_ folders, if the code is modified after execution and test is runned    

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn app.main:app --reload --host 127.0.0.1  --port 9500

# 3. Testing
python -m pytest -v or pytest -v

# 4. Testing the swagger UI
python run.py --> this will start the server on http://localhost:9500/api/docs

# 5. Seed the database (Optional)
python seed.py

# 6. Testing Seeded database (Optional)
python -m pytest tests/test_seed.py -v

# 7. Clear Seeded data (Optional)
python clear_seed.py

