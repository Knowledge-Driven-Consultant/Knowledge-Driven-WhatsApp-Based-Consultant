import logging
from tokenize import Name
from typing import List, Dict, Any, Optional, Text

from neo4j import GraphDatabase
from pyrsistent import optional

logger = logging.getLogger(__name__)

NAME = "n4sch__name"
COMMENT = "n4sch__comment"
CLASS = "n4sch__Class"

class KnowledgeBase(object):
    def get_entities(
        self,
        entity_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 5,
    ) -> List[Dict[Text, Any]]:

        raise NotImplementedError("Method is not implemented.")

    def get_attribute_of(
        self, entity_type: Text, key_attribute: Text, entity: Text, attribute: Text
    ) -> List[Any]:

        raise NotImplementedError("Method is not implemented.")

    def validate_entity(
        self, entity_type, entity, key_attribute, attributes
    ) -> Optional[Dict[Text, Any]]:

        raise NotImplementedError("Method is not implemented.")

    def map(self, mapping_type: Text, mapping_key: Text) -> Text:

        raise NotImplementedError("Method is not implemented.")


class KnowledgeGraph(KnowledgeBase):
    """
    GraphDatabase uses a grakn graph database to encode your domain knowledege. Make
    sure to have the graph database set up and the grakn server running.
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
        self.password = password
        # self.attribute_mapping = {
        #     "what is": "n4sch__comment",
        #     "What is": "n4sch__comment",
        # }
        # self.entity_type_mapping = {"business model": "BusinessModel"}

    def close(self):
        self.driver.close()

    def _thing_to_dict(self, thing):
        """
        Converts a thing (a neo4j object) to a dict for easy retrieval of the thing's
        attributes.
        """
        entity = {"id": thing.id, "type": list(thing.labels)[0]}
        for prop, val in thing.items():
            entity[prop] = val
        return entity

    def _relation_to_dict(self, rel):
        """
        convert a given neo4j relationship object to a dict for easy retrieval
        rel: relationship object
        """

        entity = {"id": rel.id, "type": rel.type}
        for prop, val in rel.items():
            entity[prop] = val
        return entity

    def _execute_entity_query(self, query: Text) -> List[Dict[Text, Any]]:
        """
        Executes a query that returns a list of entities with all their attributes in dict form
        """
        with self.driver.session() as session:
            print("Executing Cypher Query: " + query)
            result_iter = session.run(query)
            # concepts = result_iter.collect_concepts()
            entities = []
            for record in result_iter:
                entities.append(self._thing_to_dict(record["n"]))
            return entities

    def _execute_attribute_query(self, query: Text) -> List[Any]:
        """
        Executes a query that returns the value(s) an entity has for a specific
        attribute.
        """

        # this function converts new lines to \n we have to keep this in mind while parsing
        with self.driver.session() as session:
            print("Executing Cypher Query: " + query)
            result_iter = session.run(query)
            return list(result_iter.single())

    def _execute_relation_query(
        self, query: Text
    ) -> List[Dict[Text, Any]]:
        """
        Execute a query that retrives relationships. All attributes of the relation and
        all entities participating in the relation are part of the result. The entities are represented
        as start and end keys

        """
        with self.driver.session() as session:
            print("Executing Cypher Query: " + query)
            result_iter = session.run(query)

            relations = []
            relationships = []
            relation = {}
            nodes = []

            for concept in result_iter:
                relationships.append(concept["r"])
            for thing in relationships:
                relation = self._relation_to_dict(thing)
                for node in thing.nodes:
                    node = self._thing_to_dict(node)
                    nodes.append(node)
                relation["start"] = nodes[0]
                relation["end"] = nodes[1]
                relations.append(relation)

            return relations

    def get_attribute_of(self, entity: Text, attribute: Text) -> List[Any]:
        """
        Get the value of the given attribute for the provided entity.
        :param entity_type: entity type
        :param key_attribute: key attribute of entity
        :param entity: name of the entity
        :param attribute: attribute of interest
        :return: the value of the attribute
        """
        # me_clause = self._get_me_clause(entity_type)

        return self._execute_attribute_query(
            f"""
              match (n {{n4sch__name: "{entity}"}})
              return n.{attribute}
            """
        )

    def get_direct_relation_of(self, entity_type: Text = "", rel_type: Text = "", attributes: Optional[Dict[Text, Text]] = None
    ) -> List[Dict[Text, Any]]:
        """
        Given a relationship and an entity, get all entities that have that relationship with the given
        entity.
        :param entity_type: entity type
        :param attributes: any attributes of the entity (incl name)
        :param rel_type: the type (name) of relationship
        :return: list of entities (with all their attributes)
        """
        if rel_type:
            rel_type = ':' + rel_type
        if entity_type:
            entity_type = ':' + entity_type
        attr = ""
        if attributes:
            attr = "{ "
            for key, value in attributes.items():
                attr = f"{attr} {key}: '{value}'"
            attr = attr + " }"
        return self._execute_entity_query(
            f"""
              match (a{entity_type} {attr})-[r{rel_type}]-(n)
              return n
            """
        )

    def get_entities(
        self, entity_type = "", attributes: Optional[Dict[Text, Text]] = None
    ) -> List[Dict[Text, Any]]:
        """
        Given a relationship and an entity, get all entities that have that relationship with the given
        entity.
        :param entity_type: entity type
        :param attributes: any attributes of the entity (incl name)
        :param rel_type: the type (name) of relationship
        :return: list of entities (with all their attributes)
        """        
        attr = ""
        if entity_type:
            entity_type = ':' + entity_type
        if attributes:
            attr = "{ "
            for key, value in attributes.items():
                attr = f"{attr} {key}: '{value}'"
            attr = attr + " }"
        return self._execute_entity_query(
            f"""
             match (n{entity_type} {attr} ) return n 
            """
        )

    # def get_all_relations(self, entity_type: Text, entity: Text):

    #     return self._execute_relation_query(
    #         f"""
    #           match (n:{entity_type} {{n4sch__name: "{entity}"}})-[r]-(m)
    #           return *
    #         """
    #     )

    def get_type(self, entity_name):

        """
        given an entity name, return type of the entity
        """
        entity = self.get_entities(attributes={NAME:entity_name})
        return entity[0]["type"]

    def get_sibling_entities(self, entity_type: Text = "", attributes: Optional[Dict[Text, Text]] = None):
        """
        given an entity type, or an attribute such as an entity's name, get all other entities of the
        same type (sibings)
        :param entity_type: entity type
        :param attributes: any attributes of the entity (incl name)
        return: list of entities of the same type as the given entity or entity type
        """
        
        if entity_type:
            sibling_entities = self.get_entities(entity_type)
        else:
            entity = self.get_entities(entity_type, attributes)
            for ent in entity:
                ent_type = ent["type"]
                sibling_entities = self.get_entities(ent_type)
        return sibling_entities

    def get_relations(self, rel_type = "", entity_type = "", attributes: Optional[Dict[Text, Text]] = None 
    ):
        """
        get relationships with start and end entities
        :param rel_type: type of relationship
        :param entity_type: type of one of the entities involved in the relationship
        :param attributes: any attributes of the entity (incl name)
        return: dictionary containing relationships with start and end keys representing the end nodes
        of the relationship
        """
        if rel_type:
            rel_type = ':' + rel_type
        if entity_type:
            entity_type = ':' + entity_type
        attr = ""
        if attributes:
            attr = "{ "
            for key, value in attributes.items():
                attr = f"{attr} {key}: '{value}'"
            attr = attr + " }"
        return self._execute_relation_query(
            f"""
              match (n{entity_type} {attr})-[r{rel_type}]-(m)
              return *
            """
        )


    # def map(self, mapping_type: Text, mapping_key: Text) -> Text:
    #     """
    #     Query the given mapping table for the provided key.
    #     :param mapping_type: the name of the mapping table
    #     :param mapping_key: the mapping key
    #     :return: the mapping value
    #     """

    #     if (
    #         mapping_type == "attribute-mapping"
    #         and mapping_key in self.attribute_mapping
    #     ):
    #         return self.attribute_mapping[mapping_key]

    #     if (
    #         mapping_type == "entity-type-mapping"
    #         and mapping_key in self.entity_type_mapping
    #     ):
    #         return self.entity_type_mapping[mapping_key]


if __name__ == "__main__":
    q = KnowledgeGraph(
        "neo4j+s://147e2688.databases.neo4j.io",
        "neo4j",
        "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
    )
    print(q.get_sibling_entities(attributes={NAME: "CreditRisk"}))
    # print(q.get_entities("n4sch__Class", {"n4sch__name": "PaymentMethod"}))
    q.close()
