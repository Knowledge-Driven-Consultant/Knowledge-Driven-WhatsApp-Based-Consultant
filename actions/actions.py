# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from schema import schema
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from graph_database import KnowledgeGraph
import logging

logger = logging.getLogger(__name__)


def get_entity_type(tracker: Tracker) -> Text:
    """
    Get the entity type mentioned by the user. As the user may speak of an
    entity type in plural, we need to map the mentioned entity type to the
    type used in the knowledge base.
    :param tracker: tracker
    :return: entity type (same type as used in the knowledge base)
    """
    graph_database = KnowledgeGraph(
        "neo4j+s://147e2688.databases.neo4j.io",
        "neo4j",
        "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
    )
    entity_type = tracker.get_slot("entity_type")
    return graph_database.map("entity-type-mapping", entity_type)


class ActionQueryAttribute(Action):
    def name(self) -> Text:
        return "action_query_attribute"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # name = get_entity_type(tracker)

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        for entity in tracker.latest_message["entities"]:
            if schema[entity["entity"]] == "entity":
                entity_name = entity["entity"]
            if schema[entity["entity"]] == "relationship":
                relation_name = entity["entity"]
            if schema[entity["entity"]] == "attribute":
                attribute = entity["entity"]
        print(tracker.latest_message)
        value = q.get_attribute_of(entity_name, attribute)
        print(value)
        if value is not None:
            dispatcher.utter_message(f"'{value[0]}'.")
        else:
            dispatcher.utter_message(
                f"Did not found a valid value for entity '{entity_name}'."
            )

        return []

class ActionQueryEntities(Action):
    def name(self) -> Text:
        return "action_query_entities"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # name = get_entity_type(tracker)

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        for entity in tracker.latest_message["entities"]:
            if schema[entity["entity"]] == "entity":
                entity_name = entity["entity"]
            if schema[entity["entity"]] == "relationship":
                relation_name = entity["entity"]
            if schema[entity["entity"]] == "attribute":
                attribute = entity["entity"]
        print(tracker.latest_message)
        value = q.get_entities("n4sch__Class", {"n4sch__name": entity_name})
        print(value)
        if value is not None:
            dispatcher.utter_message(f"'{value[0]['n4sch__comment']}'.")
        else:
            dispatcher.utter_message(
                f"Did not found a valid value for entity '{entity_name}'."
            )

        return []

class ActionQueryRelationship(Action):
    def name(self) -> Text:
        return "action_query_relationship"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # name = get_entity_type(tracker)

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        for entity in tracker.latest_message["entities"]:
            if schema[entity["entity"]] == "entity":
                entity_name = entity["entity"]
            if schema[entity["entity"]] == "relationship":
                relation_name = entity["entity"]
                relation_value = entity["value"]
            if schema[entity["entity"]] == "attribute":
                attribute = entity["entity"]
        
        print(tracker.latest_message)
        value = q.get_direct_relation_of("n4sch__Class", entity_name, relation_name)
        print(value)
        text = f"These are the {relation_value}:\n"
        if value is not None:
            for node in value:
                text = text + node["n4sch__comment"]+ "\n"
            print(type(text))
            dispatcher.utter_message(f"{text}")
        else:
            dispatcher.utter_message(
                f"Did not found a valid value for entity '{entity_name}'."
            )

        return []