from app.retrieval.datasets import BenchmarkEntry

GOLDEN_DATASET = [
    BenchmarkEntry(
        query="movie where dreams collapse",
        expected_movie_ids=[27205],  # Inception
        expected_strategy="hybrid",
        expected_databases=["postgres", "chromadb"],
        minimum_confidence=0.7,
        expected_keywords=["dream", "collapse", "inception"]
    ),
    BenchmarkEntry(
        query="movie with spinning top totem",
        expected_movie_ids=[27205],  # Inception
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["totem", "spinning", "top"]
    ),
    BenchmarkEntry(
        query="movie where gravity bends in space",
        expected_movie_ids=[157336],  # Interstellar
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["gravity", "interstellar", "space"]
    ),
    BenchmarkEntry(
        query="Christopher Nolan movie about magic",
        expected_movie_ids=[1124],  # The Prestige
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["prestige", "magic", "nolan"]
    ),
    BenchmarkEntry(
        query="movie with the Joker and Hans Zimmer soundtrack",
        expected_movie_ids=[155],  # The Dark Knight
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["joker", "knight", "zimmer"]
    ),
    BenchmarkEntry(
        query="non-linear movie about memory loss",
        expected_movie_ids=[77],  # Memento
        expected_strategy="hybrid",
        minimum_confidence=0.6,
        expected_keywords=["memento", "memory", "nolan"]
    ),
    BenchmarkEntry(
        query="philosophical sci-fi where reality is a simulation",
        expected_movie_ids=[603],  # The Matrix
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["matrix", "simulation", "reality"]
    ),
    BenchmarkEntry(
        query="movie about alien languages",
        expected_movie_ids=[329865],  # Arrival
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["arrival", "alien", "languages"]
    ),
    BenchmarkEntry(
        query="movie with Tyler Durden",
        expected_movie_ids=[550],  # Fight Club
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["fight", "club", "durden"]
    ),
    BenchmarkEntry(
        query="social class thriller with a hidden basement",
        expected_movie_ids=[496243],  # Parasite
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["parasite", "basement", "class"]
    ),
    BenchmarkEntry(
        query="movie about an intense jazz drummer",
        expected_movie_ids=[244786],  # Whiplash
        expected_strategy="hybrid",
        minimum_confidence=0.7,
        expected_keywords=["whiplash", "jazz", "drummer"]
    )
]
