from app import db

class Casino(db.Model):
    __tablename__ = "casinos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    db_name = db.Column(db.String(100), nullable=False)
    recommender_type = db.Column(db.String(30))
    recommendation_schema = db.Column(db.JSON)
    timestamp = db.Column(db.String(30), nullable = False)
    
    def __repr__(self):
        return f"<Casino {self.id} - {self.db_name}>"
