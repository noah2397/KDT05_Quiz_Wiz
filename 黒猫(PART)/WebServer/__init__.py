from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()
migrate=Migrate()

def create_app():
    app = Flask(__name__)
    print(f'__name__ : {__name__}')
    
    app.config.from_pyfile('config.py') # 설정 내용 로딩 
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .views import main_views
    app.register_blueprint(main_views.bp)
    return app