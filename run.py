# Import app
from scrs import app
from waitress import serve

# Then simply run it
serve(app, listen="*:5000")
