import sys
import os

# Add the parent directory to sys.path so we can import 'backend'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.main import app
