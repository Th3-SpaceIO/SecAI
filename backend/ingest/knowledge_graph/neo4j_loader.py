from neo4j import GraphDatabase
from typing import List, Dict, Any
import os

class Neo4jLoader:
    """Manages the population of the Neo4j Knowledge Graph."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

    def connect(self):
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        if self.driver:
            self.driver.close()

    def create_entity(self, label: str, name: str, properties: Dict[str, Any] = None):
        """Creates or updates a node in the graph."""
        props = properties or {}
        props["name"] = name
        
        query = (
            f"MERGE (n:{label} {{name: $name}}) "
            "SET n += $props "
            "RETURN n"
        )
        
        with self.driver.session() as session:
            session.run(query, name=name, props=props)

    def create_relationship(
        self, 
        source_label: str, 
        source_name: str, 
        target_label: str, 
        target_name: str, 
        rel_type: str
    ):
        """Creates a relationship between two existing or new nodes."""
        query = (
            f"MERGE (a:{source_label} {{name: $source_name}}) "
            f"MERGE (b:{target_label} {{name: $target_name}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "RETURN r"
        )
        
        with self.driver.session() as session:
            session.run(
                query, 
                source_name=source_name, 
                target_name=target_name
            )

    def load_extracted_data(self, entities: Dict[str, List[str]], relationships: List[Dict[str, Any]]):
        """Batch loads entities and relationships into Neo4j."""
        self.connect()
        
        # Load Entities
        for label, names in entities.items():
            for name in names:
                self.create_entity(label, name)
                
        # Load Relationships
        for rel in relationships:
            self.create_relationship(
                rel["source_type"], rel["source"],
                rel["target_type"], rel["target"],
                rel["type"]
            )
