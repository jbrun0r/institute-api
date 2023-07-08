import os

from app import blueprint
from app.main import create_app, db
from app.main.util.api_error import APIError

env_name = os.environ.get("ENV_NAME", "dev")

app = create_app(env_name)
app.register_blueprint(blueprint)
app.app_context().push()


@app.cli.command("setup_api_database")
def create_db():
    db.drop_all()
    db.create_all()
    APIError.add_errors_to_database()
    db.session.commit()


if __name__ == "__main__":
    app.run(host=app.config["HOST"])
