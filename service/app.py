import os
from flask import Flask, jsonify
from service import models

# Create Flask application
app = Flask(__name__)

# Get bindings from the environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')
# HOSTNAME = os.getenv('HOSTNAME', '127.0.0.1')
# REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Application Routes
@app.route('/')
def index():
    """ Returns a message about the service """
    return jsonify(name='Hello wishlists world!', version='1.0'), 200

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":  
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
