from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from celery import Celery

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)


	from main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix='/auth')

	with app.app_context():
		# Extensions like Flask-SQLAlchemy now know what the "current" app
		# is while within this block. Therefore, you can now run........
		db.create_all()
		
	return app

def create_celery_app(app=None):
	app = app or create_app('default')
	celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
	celery.conf.update(app.config)
	Taskbase = celery.Task

	class ContextTask(Taskbase):
		abstract = True

		def __call__(self, *args, **kwargs):
			with app.app_context():
				return Taskbase.__call__(self, *args, **kwargs)
	
	celery.Task = ContextTask
	return celery
