from typing import List, Dict, Any, Tuple
from neo4j import GraphDatabase
from app.core.interfaces.graph import BaseKnowledgeGraph
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("app.providers.graph.neo4j")

class Neo4jKnowledgeGraph(BaseKnowledgeGraph):
    """
    Neo4j Graph Database provider implementing BaseKnowledgeGraph.
    """
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None
        
        # Proactively check connection on initialization
        try:
            self._connect()
        except Exception as e:
            logger.warning(
                f"Could not connect to Neo4j on startup ({self.uri}). "
                f"Application will run, but graph operations will fail. Error: {e}"
            )

    def _connect(self):
        if not self._driver:
            logger.info(f"Initializing Neo4j driver connection to {self.uri}")
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )

    @property
    def driver(self):
        if not self._driver:
            self._connect()
        return self._driver

    def execute_query(self, query: str, parameters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Executing Cypher query: {query[:80]}...")
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j execute_query failed: {e}")
            raise

    def run_transaction(self, cypher_queries: List[Tuple[str, Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        try:
            logger.info(f"Running Neo4j transaction containing {len(cypher_queries)} queries")
            results = []
            with self.driver.session() as session:
                # Execute in an explicit transaction block
                with session.begin_transaction() as tx:
                    for cypher, params in cypher_queries:
                        res = tx.run(cypher, params or {})
                        results.append([record.data() for record in res])
                    tx.commit()
            return results
        except Exception as e:
            logger.error(f"Neo4j run_transaction failed: {e}")
            raise

    def check_connection(self) -> bool:
        try:
            # Run simple query to check database responsiveness
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS val")
                record = result.single()
                return record is not None and record["val"] == 1
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

    def close(self) -> None:
        if self._driver:
            logger.info("Closing Neo4j driver connection")
            self._driver.close()
            self._driver = None
