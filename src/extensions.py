from flask_migrate import Migrate
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
sock = Sock()
swagger = Swagger()