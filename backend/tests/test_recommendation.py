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


from app.recommendation.plugins import plugin_registry
from app.recommendation.plugins.collaborative import collaborative_plugin
from app.recommendation.plugins.graph_walk import graph_walk_plugin
from app.recommendation.interfaces.plugin import BaseRecommendationPlugin
from app.retrieval.query_trace import QueryTrace

def test_plugin_registry():
    # Verify auto-discovered plugins
    plugins = plugin_registry.list_plugins()
    plugin_names = [p.name for p in plugins]
    assert "collaborative_filtering" in plugin_names
    assert "graph_walk" in plugin_names
    
    # Custom dummy plugin registration test
    class DummyPlugin(BaseRecommendationPlugin):
        @property
        def name(self) -> str:
            return "dummy_plugin"
        async def generate_candidates(self, user_id, limit, db, trace):
            return [{"movie_id": 9999, "score": 0.5, "provenance_reason": "dummy"}]
            
    dummy = DummyPlugin()
    plugin_registry.register(dummy)
    assert plugin_registry.get_plugin("dummy_plugin") == dummy

@pytest.mark.asyncio
async def test_collaborative_plugin_execution(db_session):
    # Setup similar user tastes mapping
    # user_cf_1 likes movie 10001
    # user_cf_2 also likes movie 10001 AND likes movie 10002
    
    db_session.add_all([
        UserInteractionHistory(user_id="user_cf_1", movie_id=10001, interaction_type="bookmark", created_at=datetime.utcnow()),
        UserInteractionHistory(user_id="user_cf_2", movie_id=10001, interaction_type="bookmark", created_at=datetime.utcnow()),
        UserInteractionHistory(user_id="user_cf_2", movie_id=10002, interaction_type="rating", rating=5.0, created_at=datetime.utcnow())
    ])
    db_session.commit()
    
    trace = QueryTrace(session_id="test_cf")
    candidates = await collaborative_plugin.generate_candidates(
        user_id="user_cf_1",
        limit=5,
        db=db_session,
        trace=trace
    )
    
    assert len(candidates) >= 1
    assert candidates[0]["movie_id"] == 10002
    assert candidates[0]["score"] == 1.0
    assert "similar watch profiles" in candidates[0]["provenance_reason"]

@pytest.mark.asyncio
async def test_graph_walk_plugin_execution(db_session):
    # Create movies sharing the same Sci-Fi genre (id 888)
    movie_a = Movie(id=101, tmdb_id="10001", title="Sci-Fi Movie A", popularity=50.0, release_year=2020, overview="Sci-Fi A")
    movie_b = Movie(id=102, tmdb_id="10002", title="Sci-Fi Movie B", popularity=60.0, release_year=2021, overview="Sci-Fi B")
    genre = db_session.query(Genre).filter(Genre.id == 888).first()
    if not genre:
        genre = Genre(id=888, name="Sci-Fi")
        db_session.add(genre)
    
    db_session.add_all([movie_a, movie_b])
    db_session.commit()
    
    movie_a.genres.append(genre)
    movie_b.genres.append(genre)
    db_session.commit()
    
    # user_gw bookmarks movie_a (10001)
    db_session.add(UserInteractionHistory(
        user_id="user_gw",
        movie_id=10001,
        interaction_type="bookmark",
        created_at=datetime.utcnow()
    ))
    db_session.commit()

    # Diagnostic prints
    all_movies = db_session.query(Movie).all()
    print("\n[DIAGNOSTIC] All Movies:", [(m.id, m.tmdb_id, m.title) for m in all_movies])
    for m in all_movies:
        print(f"Movie {m.title} genres: {[g.name for g in m.genres]}")
    all_genres = db_session.query(Genre).all()
    print("[DIAGNOSTIC] All Genres:", [(g.id, g.name) for g in all_genres])
    all_interactions = db_session.query(UserInteractionHistory).all()
    print("[DIAGNOSTIC] All Interactions:", [(i.user_id, i.movie_id, i.interaction_type) for i in all_interactions])
    
    # Query liked movie details matching fallback logic
    liked_movie_details = db_session.query(Movie).filter(Movie.tmdb_id.in_(["10001"])).all()
    print("[DIAGNOSTIC] Liked Movie Details matching '10001':", [(m.id, m.title) for m in liked_movie_details])

    trace = QueryTrace(session_id="test_gw")
    candidates = await graph_walk_plugin.generate_candidates(
        user_id="user_gw",
        limit=5,
        db=db_session,
        trace=trace
    )
    
    print("[DIAGNOSTIC] Candidates returned:", candidates)
    
    assert len(candidates) >= 1
    candidate_ids = [c["movie_id"] for c in candidates]
    assert 10002 in candidate_ids
    
    cand_10002 = next(c for c in candidates if c["movie_id"] == 10002)
    assert "shares 1 genres" in cand_10002["provenance_reason"].lower()


from app.recommendation.scorer import multi_stage_scorer
from app.recommendation.policies import policy_chain, AgeContentPolicy, RegionalPolicy, SubscriptionPolicy
from app.recommendation.guardrails import recommendation_guardrails, FilterBubbleBreaker
from app.recommendation.explainability import recommendation_explainer

def test_multi_stage_scorer_weights(db_session):
    # Setup movies with different release years and popularities
    movie_a = Movie(id=201, tmdb_id="20001", title="Old Unpopular Film", popularity=1.0, release_year=1990, overview="Old")
    movie_b = Movie(id=202, tmdb_id="20002", title="New Popular Film", popularity=150.0, release_year=2025, overview="New")
    db_session.add_all([movie_a, movie_b])
    db_session.commit()
    
    candidates = [
        {"movie_id": 20001, "score": 0.8, "provenance_reason": "test"},
        {"movie_id": 20002, "score": 0.8, "provenance_reason": "test"}
    ]
    
    user_features = {"genre_weights": {"Sci-Fi": 0.9}}
    scored = multi_stage_scorer.score_candidates(candidates, user_features, db_session)
    
    assert len(scored) == 2
    # The new popular movie (20002) should have a higher final score due to popularity and freshness boost
    assert scored[0]["movie_id"] == 20002

def test_diversification_mmr():
    scored_candidates = [
        {"movie_id": 1, "final_score": 0.9, "genres": ["Sci-Fi", "Action"]},
        {"movie_id": 2, "final_score": 0.8, "genres": ["Sci-Fi"]},
        {"movie_id": 3, "final_score": 0.7, "genres": ["Drama", "Romance"]}
    ]
    
    diversified = multi_stage_scorer.diversify_candidates(scored_candidates, limit=2, lambda_factor=0.5)
    assert len(diversified) == 2
    # The second slot should select movie 3 (Drama/Romance) instead of movie 2 (Sci-Fi) due to genre redundancy penalties
    assert diversified[1]["movie_id"] == 3

def test_policy_chain_filtering():
    candidates = [
        {"movie_id": 1, "adult": True, "available_countries": ["US"], "premium_only": False},
        {"movie_id": 2, "adult": False, "available_countries": ["UK"], "premium_only": False},
        {"movie_id": 3, "adult": False, "available_countries": ["US"], "premium_only": True}
    ]
    
    # 1. Child profile content filter
    child_context = {"is_child_profile": True}
    filtered_age = AgeContentPolicy().filter(candidates, child_context)
    assert len(filtered_age) == 2
    assert 1 not in [c["movie_id"] for c in filtered_age]

    # 2. Regional filter
    uk_context = {"region": "UK"}
    filtered_region = RegionalPolicy().filter(candidates, uk_context)
    assert len(filtered_region) == 1
    assert filtered_region[0]["movie_id"] == 2

    # 3. Subscription filter
    free_context = {"subscription_tier": "free"}
    filtered_sub = SubscriptionPolicy().filter(candidates, free_context)
    assert len(filtered_sub) == 2
    assert 3 not in [c["movie_id"] for c in filtered_sub]

def test_filter_bubble_breaker():
    final_list = [
        {"movie_id": 1, "genres": ["Sci-Fi"], "final_score": 0.9},
        {"movie_id": 2, "genres": ["Sci-Fi"], "final_score": 0.8}
    ]
    all_candidates = [
        {"movie_id": 1, "genres": ["Sci-Fi"], "final_score": 0.9},
        {"movie_id": 2, "genres": ["Sci-Fi"], "final_score": 0.8},
        {"movie_id": 3, "genres": ["Romance"], "final_score": 0.6}
    ]
    user_features = {"genre_weights": {"Sci-Fi": 0.9, "Romance": 0.1}}
    
    # With exploration ratio=0.5, at least 1 slot should be swapped
    bubble_breaker = FilterBubbleBreaker(exploration_ratio=0.5)
    adjusted = bubble_breaker.break_bubble(final_list, all_candidates, user_features)
    
    assert len(adjusted) == 2
    # The lowest ranking slot (index 1) should be replaced by movie 3
    assert adjusted[1]["movie_id"] == 3
    assert "exploration" in adjusted[1]["provenance_reason"].lower()

def test_explainer_explanations():
    candidate_sci_fi = {
        "movie_id": 20002,
        "title": "Sci-Fi Film",
        "genres": ["Sci-Fi"],
        "provenance_reason": "test"
    }
    user_features = {"genre_weights": {"Sci-Fi": 0.8}}
    
    expl = recommendation_explainer.generate_explanation(candidate_sci_fi, user_features)
    assert "enjoy Sci-Fi films" in expl["explanation"]
