from app import create_app, db
from app.services import populate_db


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        populate_db()
    
    app.run(debug=True)
       