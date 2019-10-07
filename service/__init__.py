"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
# import os
# import sys
# import logging
# from flask import Flask

# Get configuration from environment
# DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://postgres:postgres@localhost:5432/postgres')
# SECRET_KEY = os.getenv('SECRET_KEY', 's3cr3t-key-shhhh')

# Create Flask application
# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = SECRET_KEY

# Import the rutes After the Flask app is created
# from service import service, models

# Set up logging for production
# service.initialize_logging()

# app.logger.info(70 * '*')
# app.logger.info('  P E T   S E R V I C E   R U N N I N G  '.center(70, '*'))
# app.logger.info(70 * '*')

# app.logger.info('Service inititalized!')
