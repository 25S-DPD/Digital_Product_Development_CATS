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
        print(f"patient id action summary {patient_id}")

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
        lab_access_dict = tracker.get_slot("exams_passwords") or {}
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
        dispatcher.utter_message(text=f"Imaging Lab Access Details: {lab_access_dict}")
        dispatcher.utter_message(text=f"Recent Hospitalization: {recent_hosp}")

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
        self.token = tracker.get_slot("token")
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
            "recent_hospitalization_status": tracker.get_slot("recent_hospitalization_status")
        }

        self.save_to_database(patient_id, data)
        dispatcher.utter_message("Your medical history has been saved.")
        return []
    
    def save_to_database(self, patient_id: str, data: Dict[str, Any]):
        print(f"Saving data for patient {patient_id} to the database...")
        # TODO add the token in the pot requests
        url = f"https://redcore-latest.onrender.com/patients/{patient_id}/pre-anamnesis"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }        

        payload = {
            "chronic_disease": data.get("chronic_disease"),
            "smoking": data.get("smoking_info"),
            "medicines": data.get("medicine_info"),
            #"hospital_history": data.get("hospital_info"),
            "allergies": data.get("allergies_info"),
            "existing_illness": data.get("hereditary_disease"),
            "alcohol_drug_use": data.get("alcohol_info"),
            #"drug_use": data.get("drug_use"),
            "sleep_diet": data.get("sleep_diet"),
            "pregnancy_history": data.get("pregnancy_history"),
            #"recent_exams": data.get("recent_exams"),
            "recent_exams": [], 
            #"exams_passwords": data.get("imaging_lab_access"),
            "exam_passwords": {"hemograma.pdf": "senha123", "raio_x.jpg": "abc456", "ressonancia.pdf": "xyz789"},
            "recent_hospitalization": data.get("recent_hospitalization_status")
            #"recent_hospitalization": True
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

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
        token = tracker.get_slot("token")
        print(f"Checking patient data for ID: {patient_id}")

        if not patient_id:
            dispatcher.utter_message(text="Something went wrong! Make sure to access this chat through the proper link sent to you per email.")
            return []

        if not token:
            dispatcher.utter_message(text="Something went wrong! Make sure to access this chat through the proper link sent to you per email.")
            return []

        url = f"https://redcore-latest.onrender.com/patients/{patient_id}/pre-anamnesis-token"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                if not data:
                    dispatcher.utter_message(text="No existing record found. Let's fill out the medical history.")
                    return [SlotSet("patient_id", patient_id), FollowupAction("medical_history_form")]

                # Handle recent_hospitalization conversion
                hospitalization_status = data.get("recent_hospitalization")
                if hospitalization_status is True:
                    hospitalization_text = "Yes"
                elif hospitalization_status is False:
                    hospitalization_text = "No"
                else:
                    hospitalization_text = None
                    hospitalization_status = None

                # Map the JSON keys to your slot names
                slot_mapping = {
                    "chronic_disease": data.get("chronic_disease"),
                    "smoking_info": data.get("smoking"),
                    "medicine_info": data.get("medicines"),
                    # TODO add hospital_info to database
                    #"hospital_info": data.get("hospital_history"),
                    "allergies_info": data.get("allergies"),
                    "hereditary_disease": data.get("existing_illness"),
                    "alcohol_info": data.get("alcohol_drug_use"),
                     # TODO add drug_use to database
                    #"drug_use": data.get("drug_use"),
                    "sleep_diet": data.get("sleep_diet"),
                    "pregnancy_history": data.get("pregnancy_history"),
                    "recent_exams": data.get("recent_exams"),
                    "imaging_lab_access": data.get("exam_passwords"),
                    "recent_hospitalization": hospitalization_text,
                    "recent_hospitalization_status": hospitalization_status,
                }

                slot_sets = [SlotSet(key, value) for key, value in slot_mapping.items()]
                slot_sets.append(SlotSet("patient_id", patient_id))

                dispatcher.utter_message(text="I found your existing medical history.")
                return slot_sets + [FollowupAction("action_summary")]

            else:
                #print(f"Failed to retrieve data. Status code: {response.status_code}, Response: {response.text}")
                #dispatcher.utter_message(text="ERROR: Unable to retrieve your medical history. Please try again later.")
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

    async def validate_sleep_diet(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate sleep_diet value and handle gender-based pregnancy logic."""
    
        gender = tracker.get_slot("gender")
        
        
        # If gender is male, set pregnancy_history to N/A
        if gender and gender.lower() in ["male", "m", "man"]:
  
            return {
                "sleep_diet": slot_value,
                "pregnancy_history": "N/A"
            }
        else:
            
            return {"sleep_diet": slot_value}

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
        
        # Check if pregnancy_history should be skipped for males
        gender = tracker.get_slot("gender")
        pregnancy_history = tracker.get_slot("pregnancy_history")
        
        if (gender and gender.lower() in ["male", "m", "man"] and 
            pregnancy_history == "N/A" and 
            next_slot == "pregnancy_history"):
            
            # Find the next slot after pregnancy_history
            required_slots = await self.required_slots(
                domain.get("slots", {}), dispatcher, tracker, domain
            )
            try:
                pregnancy_index = required_slots.index("pregnancy_history")
                # Return the next slot after pregnancy_history
                if pregnancy_index + 1 < len(required_slots):
                    return required_slots[pregnancy_index + 1]
                else:
                    return None
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
        """Return required slots based on gender."""
        base_slots = [
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
        
        # Get gender from tracker
        gender = tracker.get_slot("gender")
        
        # If gender is male, remove pregnancy_history from required slots
        if gender and gender.lower() in ["male", "m", "man"]:
            base_slots = [slot for slot in base_slots if slot != "pregnancy_history"]
        
        return base_slots
    
    async def validate_recent_hospitalization(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
            """Validate recent_hospitalization value."""
            
            # Handle both button payloads and direct text input
            if slot_value in ["yes", "no"] or tracker.latest_message.get('intent', {}).get('name') in ['affirm', 'deny']:
                # Map intent to text values
                if tracker.latest_message.get('intent', {}).get('name') == 'deny' or slot_value == "no":
                    text_value = "No"
                    status_value = False
                elif tracker.latest_message.get('intent', {}).get('name') == 'affirm' or slot_value == "yes":
                    text_value = "Yes"
                    status_value = True
                else:
                    # Handle direct text input
                    if slot_value and slot_value.lower() in ['yes', 'y', 'true', '1']:
                        text_value = "Yes"
                        status_value = True
                    elif slot_value and slot_value.lower() in ['no', 'n', 'false', '0']:
                        text_value = "No"
                        status_value = False
                    else:
                        dispatcher.utter_message(text="Please answer Yes or No.")
                        return {"recent_hospitalization": None}
                
                return {
                    "recent_hospitalization": text_value,
                    "recent_hospitalization_status": status_value
                }
            else:
                dispatcher.utter_message(text="Please select Yes or No.")
                return {"recent_hospitalization": None}
            

    def validate_imaging_lab_access(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Handle the initial imaging lab access question."""
        
        intent = tracker.get_intent_of_latest_message()
        
        if intent == "deny":
            dispatcher.utter_message(response="utter_no_labs_shared")
            return {
                "imaging_lab_access": "No",
                "exams_passwords": {},
                "collecting_lab_info": False
            }
        elif intent == "affirm":
            # User wants to share, start collecting lab info
            dispatcher.utter_message(response="utter_ask_current_lab_url")
            return {
                "imaging_lab_access": "Yes",
                "collecting_lab_info": True,
                "exams_passwords": {},
                "requested_slot": None  # This prevents form from moving to next slot
            }
        
        # If neither intent, keep asking
        return {"imaging_lab_access": None}

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Override to handle custom lab collection flow."""
        
        collecting_lab_info = tracker.get_slot("collecting_lab_info")
        current_lab_url = tracker.get_slot("current_lab_url")
        current_lab_password = tracker.get_slot("current_lab_password")
        
        # If we're collecting lab info, handle that flow
        if collecting_lab_info:
            # If no URL collected yet, ask for URL
            if not current_lab_url:
                dispatcher.utter_message(response="utter_ask_current_lab_url")
                return {"requested_slot": "collect_lab_url"}
            
            # If URL collected but no password, ask for password
            elif current_lab_url and not current_lab_password:
                dispatcher.utter_message(response="utter_ask_current_lab_password")
                return {"requested_slot": "collect_lab_password"}
            
            # If both collected, ask if they want to add more
            elif current_lab_url and current_lab_password:
                dispatcher.utter_message(response="utter_ask_add_more_labs")
                return {"requested_slot": "collect_add_more"}
        
        # Continue with normal form flow
        return {"requested_slot": None}

    def validate_collect_lab_url(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Collect lab URL."""
        
        user_message = tracker.latest_message.get("text", "")
        
        if user_message and user_message.strip():
            # Basic URL validation and formatting
            url = user_message.strip()
            if not url.startswith(('http://', 'https://')):
                if not url.startswith('www.'):
                    url = 'www.' + url
            
            return {
                "current_lab_url": url,
                "collect_lab_url": url,
                "requested_slot": None
            }
        
        dispatcher.utter_message(text="Please provide a valid website URL.")
        return {"collect_lab_url": None}

    def validate_collect_lab_password(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Collect lab password."""
        
        user_message = tracker.latest_message.get("text", "")
        
        if user_message and user_message.strip():
            # Get current values
            current_url = tracker.get_slot("current_lab_url")
            current_exams_passwords = tracker.get_slot("exams_passwords") or {}
            
            # Add new credentials to the dictionary
            current_exams_passwords[current_url] = user_message.strip()
            
            return {
                "current_lab_password": user_message.strip(),
                "collect_lab_password": user_message.strip(),
                "exams_passwords": current_exams_passwords,
                "requested_slot": None
            }
        
        dispatcher.utter_message(text="Please provide a valid password.")
        return {"collect_lab_password": None}

    def validate_collect_add_more(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Handle add more labs question."""
        
        intent = tracker.get_intent_of_latest_message()
        
        if intent == "affirm":
            # User wants to add more labs - reset for next iteration
            return {
                "collect_add_more": "yes",
                "current_lab_url": None,
                "current_lab_password": None,
                "collect_lab_url": None,
                "collect_lab_password": None,
                "requested_slot": None
            }
        
        elif intent == "deny":
            # User is done adding labs
            exams_passwords = tracker.get_slot("exams_passwords") or {}
            
            if exams_passwords:
                # Show summary of saved labs
                lab_count = len(exams_passwords)
                lab_urls = ", ".join(exams_passwords.keys())
                dispatcher.utter_message(
                    text=f"Great! I've saved credentials for {lab_count} lab(s): {lab_urls}"
                )
            
            dispatcher.utter_message(response="utter_labs_saved")
            
            # Clear lab collection state and continue with form
            return {
                "collect_add_more": "no",
                "collecting_lab_info": False,
                "current_lab_url": None,
                "current_lab_password": None,
                "collect_lab_url": None,
                "collect_lab_password": None,
                "requested_slot": None
            }
        
        # If unclear response, ask again
        return {"collect_add_more": None}
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
                            SlotSet("token", jwt_token), 
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
    
class ActionCollectLabUrl(Action):
    def name(self) -> Text:
        return "action_collect_lab_url"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Check if we're in lab collection mode
        if not tracker.get_slot("collecting_lab_info"):
            return []
        
        # Get the user's message
        user_message = tracker.latest_message.get("text", "")
        
        if user_message and user_message.strip():
            # Basic URL validation and formatting
            url = user_message.strip()
            if not url.startswith(('http://', 'https://')):
                if not url.startswith('www.'):
                    url = 'www.' + url
            
            # Ask for password
            dispatcher.utter_message(response="utter_ask_lab_password")
            
            return [SlotSet("current_lab_url", url)]
        
        dispatcher.utter_message(text="Please provide a valid website URL.")
        dispatcher.utter_message(response="utter_ask_lab_url")
        return []


class ActionCollectLabPassword(Action):
    def name(self) -> Text:
        return "action_collect_lab_password"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Check if we're in lab collection mode and have a URL
        if not tracker.get_slot("collecting_lab_info") or not tracker.get_slot("current_lab_url"):
            return []
        
        # Get the user's message (password)
        user_message = tracker.latest_message.get("text", "")
        
        if user_message and user_message.strip():
            # Get current values
            current_url = tracker.get_slot("current_lab_url")
            current_exams_passwords = tracker.get_slot("exams_passwords") or {}
            
            # Add new credentials to the dictionary
            current_exams_passwords[current_url] = user_message.strip()
            
            # Ask if they want to add more labs
            dispatcher.utter_message(response="utter_ask_add_more_labs")
            
            return [
                SlotSet("current_lab_password", user_message.strip()),
                SlotSet("exams_passwords", current_exams_passwords)
            ]
        
        dispatcher.utter_message(text="Please provide a valid password.")
        dispatcher.utter_message(response="utter_ask_current_lab_password")
        return []


class ActionHandleAddMoreLabs(Action):
    def name(self) -> Text:
        return "action_handle_add_more_labs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.get_intent_of_latest_message()
        
        if intent == "affirm":
            # User wants to add more labs
            dispatcher.utter_message(response="utter_ask_lab_url")
            return [
                SlotSet("current_lab_url", None),
                SlotSet("current_lab_password", None)
            ]
        
        elif intent == "deny":
            # User is done adding labs
            exams_passwords = tracker.get_slot("exams_passwords") or {}
            
            if exams_passwords:
                # Show summary of saved labs
                lab_count = len(exams_passwords)
                lab_urls = ", ".join(exams_passwords.keys())
                dispatcher.utter_message(
                    text=f"Great! I've saved credentials for {lab_count} lab(s): {lab_urls}"
                )
            
            dispatcher.utter_message(response="utter_labs_saved")
            
            return [
                SlotSet("collecting_lab_info", False),
                SlotSet("current_lab_url", None),
                SlotSet("current_lab_password", None),
                SlotSet("add_more_labs", False)
            ]
        
        # If unclear response, ask again
        dispatcher.utter_message(response="utter_ask_add_more_labs")
        return []


class ActionHandleImagingLabResponse(Action):
    def name(self) -> Text:
        return "action_handle_imaging_lab_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # This action routes to the appropriate handler based on current state
        collecting_lab_info = tracker.get_slot("collecting_lab_info")
        current_lab_url = tracker.get_slot("current_lab_url")
        current_lab_password = tracker.get_slot("current_lab_password")
        
        # If collecting lab info
        if collecting_lab_info:
            # If no URL yet, collect URL
            if not current_lab_url:
                return [FollowupAction("action_collect_lab_url")]
            # If URL but no password, collect password
            elif not current_lab_password:
                return [FollowupAction("action_collect_lab_password")]
            # If both URL and password, handle add more labs
            else:
                return [FollowupAction("action_handle_add_more_labs")]
        
        return []