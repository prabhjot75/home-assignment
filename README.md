# Refer to docs folder for more information on the requirements

# Architecture - 
#    Seperation of concern principle is followed, for a modular, domain-agnostic layered architecture

####
# Instructions
####

# a. Installing pip. This is (optional) - (I had to do it to fix my existing environment).
python -m pip install --upgrade pip setuptools wheel

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn app.main:app --reload --host 127.0.0.1  --port 9500

# 3. Testing
pytest -v


