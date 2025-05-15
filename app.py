from flask import Flask

import os
from dotenv import load_dotenv

from Controllers.auth_controller import auth_bp
from Controllers.collage_controller import collage_bp
from Controllers.recent_controller import recent_bp


# This file serves as the entry point for the application, registering the blueprints (routes)


load_dotenv()
# Setting up the app
app = Flask(__name__, template_folder='views/templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")



# Registering blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(recent_bp, url_prefix='/recent')
app.register_blueprint(collage_bp, url_prefix='/collage')



if __name__ == '__main__':
    app.run(debug=True, port=5001)