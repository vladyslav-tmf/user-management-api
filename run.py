import click

from app.app import create_app, db
from app.models import User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make flask shell context with app, db, and models."""
    return {"app": app, "db": db, "User": User}


@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables."""
    db.create_all()
    click.echo("Database initialized successfully")


if __name__ == "__main__":
    app.run(debug=True)
