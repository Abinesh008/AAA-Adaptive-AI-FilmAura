from typing import Generic, TypeVar

RepositoryType = TypeVar("RepositoryType")

class BaseService(Generic[RepositoryType]):
    """
    Base Service layer class encapsulating business rules and wrapping repository interactions.
    """
    def __init__(self, repository: RepositoryType):
        self.repo = repository
