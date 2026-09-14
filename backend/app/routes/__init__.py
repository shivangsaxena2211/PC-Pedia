from app.routes.categories import categories_bp
from app.routes.manufacturers import manufacturers_bp
from app.routes.products import products_bp
from app.routes.search import search_bp
from app.routes.compare import compare_bp
from app.routes.admin import admin_bp
from app.routes.home import home_bp


def register_blueprints(app):
    app.register_blueprint(home_bp, url_prefix="/api")
    app.register_blueprint(categories_bp, url_prefix="/api")
    app.register_blueprint(manufacturers_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(compare_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
