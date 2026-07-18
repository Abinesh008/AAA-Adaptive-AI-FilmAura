import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base_class import Base
from app.models.movie import UserPreferenceProfile, UserInteractionHistory, Movie, Genre, MovieCrew, Person
from app.recommendation.feature_store import feature_store
from app.recommendation.profile import profile_learning_engine

# Setup clean, isolated in-memory SQLite database for testing SQLAlchemy tables
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_feature_store_operations(db_session):
    # Insert dummy user preference profile
    profile = UserPreferenceProfile(
        user_id="user_123",
        genre_weights={"Sci-Fi": 0.8, "Drama": 0.3},
        favorite_directors=["Christopher Nolan"],
        favorite_actors=["Leonardo DiCaprio"],
        excluded_keywords=["slasher"]
    )
    db_session.add(profile)
    
    # Insert dummy interactions
    interaction1 = UserInteractionHistory(
        user_id="user_123",
        movie_id=27205,
        interaction_type="click",
        created_at=datetime.utcnow()
    )
    interaction2 = UserInteractionHistory(
        user_id="user_123",
        movie_id=27205,
        interaction_type="rating",
        rating=5.0,
        created_at=datetime.utcnow()
    )
    interaction3 = UserInteractionHistory(
        user_id="user_123",
        movie_id=157336,
        interaction_type="skip",
        created_at=datetime.utcnow()
    )
    
    db_session.add_all([interaction1, interaction2, interaction3])
    db_session.commit()
    
    # Test get_user_features
    features = feature_store.get_user_features("user_123", db_session)
    assert features["user_id"] == "user_123"
    assert features["genre_weights"]["Sci-Fi"] == 0.8
    assert features["total_clicks"] == 1
    assert features["total_skips"] == 1
    assert features["average_rating"] == 5.0
    assert features["interaction_count"] == 3
    
    # Test sync_offline_features
    offline_data = {
        "genre_weights": {"Sci-Fi": 0.95, "Adventure": 0.7},
        "favorite_directors": ["Denis Villeneuve"]
    }
    feature_store.sync_offline_features("user_123", offline_data, db_session)
    
    updated_profile = db_session.query(UserPreferenceProfile).filter(UserPreferenceProfile.user_id == "user_123").first()
    assert updated_profile.genre_weights["Sci-Fi"] == 0.95
    assert updated_profile.genre_weights["Adventure"] == 0.7
    assert updated_profile.favorite_directors == ["Denis Villeneuve"]

def test_profile_temporal_decay():
    # Test weight decays based on history timestamps
    now = datetime.utcnow()
    day_old = now - timedelta(days=1)
    month_old = now - timedelta(days=30)
    
    w_now = profile_learning_engine.calculate_decay_weight(now)
    w_day = profile_learning_engine.calculate_decay_weight(day_old)
    w_month = profile_learning_engine.calculate_decay_weight(month_old)
    
    assert abs(w_now - 1.0) < 0.001
    assert w_day < 1.0
    assert abs(w_month - 0.5) < 0.05  # 30 days is the half-life, so weight should be close to 0.5

def test_profile_learning_rebuild(db_session):
    # Insert mock Movie catalog data
    movie = Movie(
        id=999,
        tmdb_id="99999",
        title="Interstellar",
        popularity=85.5,
        release_year=2014,
        overview="Plot description here"
    )
    db_session.add(movie)
    db_session.commit()
    
    # Setup mapping relationships: Genre & Director
    genre = Genre(id=888, name="Sci-Fi")
    db_session.add(genre)
    db_session.commit()
    
    # Link genre to movie via association table (or direct append)
    movie.genres.append(genre)
    
    # Create Director role
    director = Person(id=777, name="Christopher Nolan", external_person_id="nolan")
    db_session.add(director)
    db_session.commit()
    
    crew_role = MovieCrew(
        id=123,
        movie_id=movie.id,
        person_id=director.id,
        job="Director",
        department="Directing"
    )
    db_session.add(crew_role)
    db_session.commit()
    
    # Add interaction events for rebuild
    interaction = UserInteractionHistory(
        user_id="user_rebuild",
        movie_id=99999,
        interaction_type="bookmark",
        created_at=datetime.utcnow()
    )
    db_session.add(interaction)
    db_session.commit()
    
    # Run rebuild profile pipeline
    profile_learning_engine.rebuild_profile("user_rebuild", db_session)
    
    profile = db_session.query(UserPreferenceProfile).filter(UserPreferenceProfile.user_id == "user_rebuild").first()
    assert profile is not None
    assert profile.genre_weights["Sci-Fi"] == 1.0
    assert "Christopher Nolan" in profile.favorite_directors
