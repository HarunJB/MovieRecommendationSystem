# Hybrid Recommendation Service
# Combines collaborative and content-based filtering

from app.services.collaborative_filtering import get_collaborative_recommendations
from app.services.content_based_filtering import get_content_based_recommendations

def get_hybrid_recommendations(user_id, n=10, cf_weight=0.6, cb_weight=0.4):
    """
    Combines collaborative filtering (60%) and content-based filtering (40%).
    Weights can be adjusted based on evaluation metrics (RMSE, precision).
    """
    
