import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get('KEY')
csrf = CSRFProtect()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SESSION_COOKIE_SAMESITE'] = 'lax'
    csrf.init_app(app)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('KEY'),
        DATABASE=os.path.join(app.instance_path, 'login_form.sqlite'),

    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    @app.after_request
    def add_security_headers(resp):
        # csp = "default-src 'self'; frame-ancestors 'self'; form-action 'self'"
        resp.headers['Content-Security-Policy'] = 'default-src \'self\'; script-src \'self\'; style-src \'self\'; frame-ancestors \'self\'; form-action \'self\''
        # resp.headers['Content-Security-Policy'] = csp
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        return resp

    return app
