from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import SlotSet, ActiveLoop, FollowupAction
import psycopg2

from dotenv import load_dotenv
import os
import requests
from typing import Dict, Any


class ActionSummary(Action):
    def name(self) -> Text:
        return "action_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        patient_id = tracker.get_slot("patient_id")
        print(f"patient id {patient_id}")

        chronic = tracker.get_slot("chronic_disease")
        smoking = tracker.get_slot("smoking_info")
        medicine = tracker.get_slot("medicine_info")
        hospital = tracker.get_slot("hospital_info")
        allergies = tracker.get_slot("allergies_info")
        hereditary = tracker.get_slot("hereditary_disease")
        alcohol = tracker.get_slot("alcohol_info")  
        drug_use = tracker.get_slot("drug_use")
        sleep_diet = tracker.get_slot("sleep_diet")
        pregnancy = tracker.get_slot("pregnancy_history")
        exams = tracker.get_slot("recent_exams")
        lab_access = tracker.get_slot("imaging_lab_access")
        recent_hosp = tracker.get_slot("recent_hospitalization")

        # Send each line as a separate message
        dispatcher.utter_message(text="Here's what I've collected so far:")

        dispatcher.utter_message(text=f"Chronic Disease: {chronic}")
        dispatcher.utter_message(text=f"Smoking Info: {smoking}")
        dispatcher.utter_message(text=f"Medicine Info: {medicine}")
        dispatcher.utter_message(text=f"Hospital Info: {hospital}")
        dispatcher.utter_message(text=f"Allergies Info: {allergies}")
        dispatcher.utter_message(text=f"Hereditary Diseases: {hereditary}")
        dispatcher.utter_message(text=f"Alcohol Info: {alcohol}")
        dispatcher.utter_message(text=f"Drug Use: {drug_use}")
        dispatcher.utter_message(text=f"Sleep and Diet: {sleep_diet}")
        dispatcher.utter_message(text=f"Pregnancy History: {pregnancy}")
        dispatcher.utter_message(text=f"Recent Exams: {exams}")
        dispatcher.utter_message(text=f"Imaging Lab Access: {lab_access}")
        dispatcher.utter_message(text=f"Recent Hospitalization Summary: {recent_hosp}")

        # Then send the question with buttons
        dispatcher.utter_message(
            text="Do you want to change anything?",
            buttons=[
                {"title": "Yes", "payload": "/affirm"},
                {"title": "No", "payload": "/deny"}
            ]
        )

        return [SlotSet("patient_id", patient_id)]



import sqlite3

class ActionSavePatientData(Action):
    def name(self) -> Text:
        return "action_save_patient_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        patient_id = tracker.get_slot("patient_id")
        print(f"id {patient_id}")

        if not patient_id:
            dispatcher.utter_message("Missing patient ID. Cannot save.")
            return []

        data = {
            "chronic_disease": tracker.get_slot("chronic_disease"),
            "smoking_info": tracker.get_slot("smoking_info"),
            "medicine_info": tracker.get_slot("medicine_info"),
            "hospital_info": tracker.get_slot("hospital_info"),
            "allergies_info": tracker.get_slot("allergies_info"),
            "hereditary_disease": tracker.get_slot("hereditary_disease"),
            "alcohol_info": tracker.get_slot("alcohol_info"),
            "drug_use": tracker.get_slot("drug_use"),
            "sleep_diet": tracker.get_slot("sleep_diet"),
            "pregnancy_history": tracker.get_slot("pregnancy_history"),
            "recent_exams": tracker.get_slot("recent_exams"),
            "imaging_lab_access": tracker.get_slot("imaging_lab_access"),
            "recent_hospitalization": tracker.get_slot("recent_hospitalization")
        }

        self.save_to_database(patient_id, data)
        dispatcher.utter_message("Your medical history has been saved.")
        return []
    def save_to_database(self, patient_id: str, data: Dict[str, Any]):
        # TODO add the token in the pot requests
        url = f"https://redcore-latest.onrender.com/patients/{patient_id}/pre-anamnesis"

        payload = {
            "chronic_disease": data.get("chronic_disease"),
            "smoking": data.get("smoking"),
            "medicines": data.get("medicines"),
            "allergies": data.get("allergies"),
            "existing_illness": data.get("existing_illness"),
            "alcohol_drug_use": data.get("alcohol_drug_use"),
            "sleep_diet": data.get("sleep_diet"),
            "pregnancy_history": data.get("pregnancy_history"),
            "recent_exams": data.get("recent_exams"), 
            "recent_hospitalization": data.get("recent_hospitalization")
        }

        try:
            response = requests.post(url, json=payload)

            if response.status_code == 200 or response.status_code == 201:
                print("Data successfully sent to API.")
            else:
                print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

        except requests.RequestException as e:
            print(f"Error during POST request: {e}")


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop, FollowupAction
from typing import Text, List, Dict, Any

class ActionCorrectSlot(Action):
    def name(self) -> Text:
        return "action_correct_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_user_msg = tracker.latest_message.get("text", "").strip().lower()
        slot_reset_map = {
            "chronic_disease": "chronic_disease",
            "smoking_info": "smoking_info",
            "medicine_info": "medicine_info",
            "hospital_info": "hospital_info",
            "allergies_info": "allergies_info",
            "hereditary_disease": "hereditary_disease",
            "alcohol_info": "alcohol_info",
            "drug_use": "drug_use",
            "sleep_diet": "sleep_diet",
            "pregnancy_history": "pregnancy_history",
            "recent_exams": "recent_exams",
            "imaging_lab_access": "imaging_lab_access",
            "recent_hospitalization": "recent_hospitalization"
        }

        if last_user_msg in slot_reset_map:
            slot_to_reset = slot_reset_map[last_user_msg]
            return [
                SlotSet(slot_to_reset, None),
                ActiveLoop("medical_history_form"),
                FollowupAction("medical_history_form")
            ]
        else:
            buttons = []
            for slot_name in slot_reset_map.keys():
                buttons.append(
                    {
                        "title": slot_name.replace("_", " ").capitalize(),
                        "payload": slot_name
                    }
                )

            dispatcher.utter_message(
                text="Which field would you like to correct? Please choose one of the options below:",
                buttons=buttons
            )
            return []



from rasa_sdk.events import SlotSet, FollowupAction
import sqlite3  # or any DB you're using

class ActionCheckPatientData(Action):
    def name(self) -> Text:
        return "action_check_patient_data"

    def run(self, dispatcher, tracker, domain):
        patient_id = tracker.get_slot("patient_id")

        if not patient_id:
            dispatcher.utter_message(text="Please provide a valid patient ID.")
            return []

        url = f"https://redcore-latest.onrender.com/patients/{patient_id}/pre-anamnesis"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()

                if not data:
                    dispatcher.utter_message(text="No existing record found. Let's fill out the medical history.")
                    return [SlotSet("patient_id", patient_id), FollowupAction("medical_history_form")]

                # Map the JSON keys to your slot names
                slot_mapping = {
                    "chronic_disease": data.get("chronic_disease"),
                    "smoking_info": data.get("smoking"),
                    "medicine_info": data.get("medicines"),
                    "allergies_info": data.get("allergies"),
                    "hereditary_disease": data.get("existing_illness"),
                    "alcohol_info": data.get("alcohol_drug_use"),
                    "sleep_diet": data.get("sleep_diet"),
                    "pregnancy_history": data.get("pregnancy_history"),
                    "recent_exams": data.get("recent_exams"),
                    # TODO add imaging lab access to database
                    "imaging_lab_access": None,
                    "recent_hospitalization": data.get("recent_hospitalization"),
                }

                slot_sets = [SlotSet(key, value) for key, value in slot_mapping.items()]
                slot_sets.append(SlotSet("patient_id", patient_id))

                dispatcher.utter_message(text="I found your existing medical history.")
                return slot_sets + [FollowupAction("action_summary")]

            else:
                dispatcher.utter_message(text="No existing record found. Let's fill out the medical history.")
                return [SlotSet("patient_id", patient_id), FollowupAction("medical_history_form")]

        except requests.RequestException as e:
            dispatcher.utter_message(text="Sorry, there was an error accessing your medical history. Please try again later.")
            return []
from typing import Dict, Text, Any, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
class ValidateMedicalHistoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_medical_history_form"

    async def validate_smoking_info(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate smoking_info value."""
        
        # Handle both button payloads and direct text input
        if slot_value in ["yes", "no", "used to"] or tracker.latest_message.get('intent', {}).get('name') in ['affirm', 'deny']:
            # Map intent to text values
            if tracker.latest_message.get('intent', {}).get('name') == 'deny':
                actual_value = "No"
            elif tracker.latest_message.get('intent', {}).get('name') == 'affirm':
                # Check if it's "Yes" or "Used to" based on button title or entity
                latest_text = tracker.latest_message.get('text', '').lower()
                if 'used to' in latest_text:
                    actual_value = "Used to"
                else:
                    actual_value = "Yes"
            else:
                # Direct text input
                actual_value = slot_value.title() if slot_value else "No"
            
            # If user doesn't smoke, set combined smoking info and skip other questions
            if actual_value == "No":
                return {
                    "smoking_info": "No",
                    "smoking_duration": "N/A",
                    "smoking_frequency": "N/A"
                }
            else:
                # Reset duration and frequency slots when changing from No to Yes/Used to
                return {
                    "smoking_info": actual_value,
                    "smoking_duration": None,  # Reset to ensure questions are asked
                    "smoking_frequency": None  # Reset to ensure questions are asked
                }
        else:
            dispatcher.utter_message(text="Please select Yes, Used to, or No.")
            return {"smoking_info": None}

    async def validate_smoking_duration(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate smoking_duration value."""
        
        # Skip if already set to N/A (user doesn't smoke)
        if slot_value == "N/A":
            return {"smoking_duration": slot_value}
            
        valid_durations = ["Less than 1", "1-5", "5-10", "10+"]
        if slot_value in valid_durations:
            return {"smoking_duration": slot_value}
        else:
            dispatcher.utter_message(text="Please select a valid option.")
            return {"smoking_duration": None}

    async def validate_smoking_frequency(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate smoking_frequency value and create combined smoking_info."""
        
        # Skip if already set to N/A (user doesn't smoke)
        if slot_value == "N/A":
            return {"smoking_frequency": slot_value}
            
        valid_frequencies = ["Less than 5", "5-10", "10-15", "15-20", "20+"]
        if slot_value in valid_frequencies:
            # Get the smoking duration that was already collected
            smoking_status = tracker.get_slot("smoking_info")
            smoking_duration = tracker.get_slot("smoking_duration")
            
            # Create combined smoking info based on smoking status
            if smoking_status == "Used to":
                combined_smoking_info = f"{smoking_status} / {smoking_duration} years / {slot_value} cigarettes per day"
            else:
                combined_smoking_info = f"{smoking_status} / {smoking_duration} years / {slot_value} cigarettes per day"
            
            return {
                "smoking_frequency": slot_value,
                "smoking_info": combined_smoking_info
            }
        else:
            dispatcher.utter_message(text="Please select a valid option (1-5 cigarettes).")
            return {"smoking_frequency": None}

    async def next_slot_to_request(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Optional[Text]:
        """Determine the next slot to request based on conditional logic."""
        
        # Get the standard next slot
        next_slot = await super().next_slot_to_request(dispatcher, tracker, domain)
        
        # Check if smoking_info is currently "No" AND we're not in the middle of changing it
        smoking_info = tracker.get_slot("smoking_info")
        
        # Only skip smoking questions if:
        # 1. smoking_info is "No"
        # 2. smoking_duration is already set to "N/A" (meaning we've processed the "No" response)
        # 3. We're trying to request smoking_duration or smoking_frequency
        smoking_duration = tracker.get_slot("smoking_duration")
        
        if (smoking_info == "No" and 
            smoking_duration == "N/A" and 
            next_slot in ["smoking_duration", "smoking_frequency"]):
            
            # Find the next slot after smoking questions
            required_slots = await self.required_slots(
                domain.get("slots", {}), dispatcher, tracker, domain
            )
            try:
                medicine_index = required_slots.index("medicine_info")
                return required_slots[medicine_index]
            except (ValueError, IndexError):
                return None
                
        return next_slot

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        """Return required slots."""
        return [
            "chronic_disease",
            "smoking_info", 
            "smoking_duration",
            "smoking_frequency",
            "medicine_info",
            "hospital_info",
            "allergies_info", 
            "hereditary_disease",
            "alcohol_info",
            "drug_use",
            "sleep_diet",
            "pregnancy_history",
            "recent_exams",
            "imaging_lab_access",
            "recent_hospitalization"
        ]
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import jwt
import logging

logger = logging.getLogger(__name__)

class ActionGreetWithJWT(Action):
    """Greet user and start medical history collection with JWT patient ID and gender"""
    
    def name(self) -> Text:
        return "action_greet_with_jwt"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        patient_id = tracker.get_slot("patient_id")
        gender = tracker.get_slot("gender")

        if not patient_id:
            try:
                metadata = tracker.latest_message.get('metadata', {})
                jwt_token = metadata.get('jwt_token') or metadata.get('authorization')

                if jwt_token and jwt_token.startswith('Bearer '):
                    jwt_token = jwt_token[7:]

                if jwt_token:
                    decoded_token = jwt.decode(
                        jwt_token,
                        options={"verify_signature": False}
                    )

                    patient_id = decoded_token.get('sub')
                    gender = decoded_token.get('gender')  

                    if patient_id:
                        logger.info(f"Extracted patient_id: {patient_id}, gender: {gender}")
                        dispatcher.utter_message(response="utter_intro")
                        return [
                            SlotSet("patient_id", patient_id),
                            SlotSet("gender", gender),  
                            FollowupAction("action_check_patient_data")
                        ]
            except Exception as e:
                logger.error(f"JWT extraction failed during greeting: {e}")

        elif patient_id:
            # Patient ID already set
            dispatcher.utter_message(response="utter_intro")
            return [FollowupAction("action_check_patient_data")]

        # If extraction failed
        dispatcher.utter_message(
            text="Sorry, I couldn't verify your identity. Please make sure you accessed this chat through the proper link with a valid authentication token."
        )
        return []
