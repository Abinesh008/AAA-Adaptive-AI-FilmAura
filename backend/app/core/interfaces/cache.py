from abc import ABC, abstractmethod

class BaseCacheManager(ABC):
    """
    Abstract interface for Caching operations.
    """
    @abstractmethod
    def get(self, key: str) -> str | None:
        """
        Retrieve a value by its key. Returns None if key does not exist.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str, expire: int | None = None) -> None:
        """
        Store a key-value pair, with an optional expiration time in seconds.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a key-value pair.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Flush all items in the cache store.
        """
        pass
