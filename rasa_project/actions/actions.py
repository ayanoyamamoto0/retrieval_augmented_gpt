# Import required libraries
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import sys
import csv
import os


# ----- Action to recommend course -----

# If the file paths are modified, please update below
current_file_path = os.path.abspath(__file__)
parent_directory = os.path.abspath(os.path.join(current_file_path, os.pardir))
grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))
target_directory = os.path.abspath(os.path.join(grandparent_directory, os.pardir))

sys.path.append(target_directory)

from part2 import chat_response

class ActionRecommendCourse(Action):
    def name(self) -> Text:
        return 'action_recommend_course'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_input = tracker.latest_message['text']
        result = chat_response(user_input)
        
        dispatcher.utter_message(text=result)
        
        return []


# ----- Action to export form information to CSV -----

class ActionExportFormToCSV(Action):
    def name(self) -> Text:
        return 'action_export_form_to_csv'

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract form input
        form_data = {
            'first_name': tracker.get_slot('first_name'),
            'last_name': tracker.get_slot('last_name'),
            'phone_number': tracker.get_slot('phone_number'),
            'email_address': tracker.get_slot('email_address'),
            'day_time': tracker.get_slot('day_time')
        }

        # Write the form data to a CSV file
        with open('callback_form_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['first_name', 'last_name', 'phone_number', 'email_address', 'day_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(form_data)

        return []

