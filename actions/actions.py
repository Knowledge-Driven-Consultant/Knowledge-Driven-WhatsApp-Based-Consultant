# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from attr import attrib

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction
from graph_database import KnowledgeGraph
import logging
import random
from schema import schema

logger = logging.getLogger(__name__)


def get_properties_from_entity(dict):
    entity_name = dict["n4sch__label"]
    property = {
        key: val
        for key, val in dict.items()
        if key
        not in [
            "id",
            "type",
            "n4sch__url",
            "n4sch__label",
            "n4sch__name",
            "n4sch__comment",
        ]
    }

    text = ""
    for key, val in property.items():
        text += f'the {key.replace("_"," ").capitalize()} of {entity_name} is {val}\n'

    return text + "\n\n"


class ActionQueryEntity(Action):
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

        if tracker.latest_message["entities"]:
            for entity in tracker.latest_message["entities"]:
                if schema[entity["entity"]] == "entity":
                    entity_name = entity["entity"]
            value = q.get_entities(attributes={"n4sch__name": entity_name})
            print(value)
            if value is not None:
                dispatcher.utter_message(f"{value[0]['n4sch__comment']}.")
            else:
                dispatcher.utter_message(
                    f"Did not found a valid value for entity '{entity_name}'."
                )
                dispatcher.utter_image_url(
                    "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
                )
        else:
            dispatcher.utter_message(
                "We cannot find what you are looking for, try something else."
            )
            dispatcher.utter_image_url(
                "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
            )

        # FollowupAction("action_trigger_sibling")


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

        if tracker.latest_message["entities"]:
            for entity in tracker.latest_message["entities"]:
                if schema[entity["entity"]] == "entity":
                    entity_name = entity["entity"]
                if schema[entity["entity"]] == "relationship":
                    relation_name = entity["entity"]
                    relation_value = entity["value"]

            value = q.get_direct_relation_of(
                rel_type=relation_name, attributes={"n4sch__name": entity_name}
            )
            text = f"Here they are:\n"

            if value is not None:
                for node in value:
                    text = text + node["n4sch__label"] + "\n"
                text = (
                    text
                    + f"If you want to know about any specific term, type its name!"
                )
                dispatcher.utter_message(f"{text}")
            else:
                dispatcher.utter_message(
                    f"Did not found a valid value for entity '{entity_name}'."
                )
                dispatcher.utter_image_url(
                    "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
                )
        else:
            dispatcher.utter_message(
                "We cannot find what you are looking for, try something else."
            )
            dispatcher.utter_image_url(
                "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
            )

        return []


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

        if tracker.latest_message["entities"]:

            for entity in tracker.latest_message["entities"]:
                if schema[entity["entity"]] == "entity":
                    entity_name = entity["entity"]
                if schema[entity["entity"]] == "attribute":
                    attribute = entity["entity"]
            value = q.get_attribute_of(entity_name, attribute)
            print(value)
            if value is not None:
                dispatcher.utter_message(f"{value[0]}.")

            else:
                dispatcher.utter_message(
                    f"Did not found a valid value for entity '{entity_name}'."
                )
                dispatcher.utter_image_url(
                    "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
                )
        else:
            dispatcher.utter_message(
                "We cannot find what you are looking for, try something else."
            )
            dispatcher.utter_image_url(
                "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
            )

        return []


class ActionCompareEntities(Action):
    def name(self) -> Text:
        return "action_compare_entities"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        if tracker.latest_message["entities"]:
            for entity in tracker.latest_message["entities"]:
                value = q.get_entities(attributes={"n4sch__name": entity["entity"]})
                dispatcher.utter_message(get_properties_from_entity(value[0]))

        else:
            dispatcher.utter_message(
                "We cannot find what you are looking for, try something else."
            )
            dispatcher.utter_image_url(
                "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
            )

        return []


class ActionTriggerSiblings(Action):
    def name(self) -> Text:
        return "action_trigger_sibling"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        entity_name = tracker.latest_message["entities"][0]["entity"]
        siblings = q.get_sibling_entities(attributes={"n4sch__name": entity_name})

        if siblings is not None:
            text = []
            for value in siblings:
                if value["n4sch__name"] != entity_name:
                    text.append(value["n4sch__label"])

            random.shuffle(text)
            print(text)
            final = "Do you want know about a similar term named: " + text[0] + "?"
            print(final)

            dispatcher.utter_message(f"{final}")

        return []


class ActionAskVocab(Action):
    def name(self) -> Text:
        return "action_ask_vocab"

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

        vocab = q.get_direct_relation_of(
            rel_type="contains", attributes={"n4sch__name": entity_name}
        )

        if vocab is not None:
            text = []
            for value in vocab:
                text.append(value["n4sch__label"])

            random.shuffle(text)
            if text:
                final = "Do you want know about a similar term named: " + text[0] + "?"
                print(final)

                dispatcher.utter_message(f"{final}")

        return []


class ActionCompareAttribute(Action):
    def name(self) -> Text:
        return "action_compare_attributes"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        if tracker.latest_message["entities"]:
            entities = {}
            for entity in tracker.latest_message["entities"]:
                if schema[entity["entity"]] == "entity":
                    entities[entity["entity"]] = "none"
                if schema[entity["entity"]] == "attribute":
                    attribute = entity["entity"]

            print(entities)
            text = ""
            for key in entities:
                value = q.get_attribute_of(key, attribute)
                text = (
                    text + f'The {attribute.replace("_"," ")} of {key} is {value[0]} \n'
                )

            dispatcher.utter_message(text)

        else:
            dispatcher.utter_message(
                "We cannot find what you are looking for, try something else."
            )
            dispatcher.utter_image_url(
                "https://i.gifer.com/origin/d3/d3137e9b40af2f14927c8282cb29ae2e_w200.gif"
            )

        return []


class ActionMatchEntities(Action):
    def name(self) -> Text:
        return "action_match_entities"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        q = KnowledgeGraph(
            "neo4j+s://147e2688.databases.neo4j.io",
            "neo4j",
            "mSVGV6yUNTVmSi0_8uyt6psAnd7c5zOhUWMGvZHr0cg",
        )

        if tracker.latest_message["entities"]:
            for entity in tracker.latest_message["entities"]:
                if schema[entity["entity"]] == "entity":
                    entity_name = entity["entity"]
                if schema[entity["entity"]] == "attribute":
                    attribute = entity["entity"]
                if schema[entity["entity"]] == "relationship":
                    relation_name = entity["entity"]
                    relation_value = entity["value"]
                if schema[entity["entity"]] == "attribute_value":
                    attribute_value = entity["entity"]

        value = q.get_direct_relation_of(
            rel_type=relation_name, attributes={"n4sch__name": entity_name}
        )

        text = f'Following have {attribute.replace("_"," ")} {attribute}\n'
        for ent in value:
            if ent[attribute] == attribute_value:
                text += ent["n4sch__label"] + "\n"

        dispatcher.utter_message(text)

        return []
