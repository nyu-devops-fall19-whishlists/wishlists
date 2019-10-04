# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0

import os
from flask import Flask, render_template

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
    return render_template('base.html')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
