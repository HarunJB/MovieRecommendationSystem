from app import db
from datetime import datetime

class UserMovieInteraction(db.Model):
    __tablename__ = 'user_movie_interaction'

    interaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    interaction_type = db.Column(db.String(20), nullable=False, default='rated')
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_onboarding = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'rating': self.rating,
            'interaction_type': self.interaction_type,
            'rated_at': self.rated_at.isoformat(),
            'is_onboarding': self.is_onboarding
        }

    def __repr__(self):
        return f'<Interaction user={self.user_id} movie={self.movie_id} rating={self.rating}>'
