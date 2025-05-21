from app import create_app, db
from app.services import populate_db
from kafka_app.init_topics import create_topics


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        populate_db()
        create_topics()
    
    app.run(debug=True, host="0.0.0.0", port=5000)
       