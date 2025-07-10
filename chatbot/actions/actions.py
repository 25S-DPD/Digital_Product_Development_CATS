from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import SlotSet, ActiveLoop, FollowupAction
import requests
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from typing import Any, Text, Dict, List
import jwt
import logging

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
        lab_access_dict = tracker.get_slot("exam_passwords") 
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
            "exam_passwords": tracker.get_slot("exam_passwords"),  
            "recent_hospitalization_status": tracker.get_slot("recent_hospitalization_status")
        }

        self.save_to_database(patient_id, data)
        dispatcher.utter_message("Your medical history has been saved.")
        return []
    
    def save_to_database(self, patient_id: str, data: Dict[str, Any]):
        print(f"Saving data for patient {patient_id} to the database...")
        
        url = f"https://redcore-latest.onrender.com/patients/{patient_id}/pre-anamnesis"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }        

        payload = {
            "chronic_disease": data.get("chronic_disease"),
            "smoking": data.get("smoking_info"),
            "medicines": data.get("medicine_info"),
            "hospital_history": data.get("hospital_info"), # column to be created in the database
            "allergies": data.get("allergies_info"),
            "existing_illness": data.get("hereditary_disease"),
            "alcohol_drug_use": data.get("alcohol_info"),
            "drug_use": data.get("drug_use"), # column to be created in the database
            "sleep_diet": data.get("sleep_diet"),
            "pregnancy_history": data.get("pregnancy_history"),
            #"recent_exams": data.get("recent_exams"), # i need to upate this
            "recent_exams": [], 
            "exams_passwords": data.get("exam_passwords"),
            "recent_hospitalization": data.get("recent_hospitalization_status")
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200 or response.status_code == 201:
                print("Data successfully sent to API.")
            else:
                print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

        except requests.RequestException as e:
            print(f"Error during POST request: {e}")



class ActionCorrectSlot(Action):
    def name(self) -> Text:
        return "action_correct_slot"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_user_msg = tracker.latest_message.get("text", "").strip().lower()
        print(f"Last user message: {last_user_msg}")
        
        # Complete slot reset map including all slots from your domain.yml
        slot_reset_map = {
            "chronic_disease": "chronic_disease",
            "smoking_info": "smoking_info",
            "smoking_duration": "smoking_duration",  # Missing slot
            "smoking_frequency": "smoking_frequency",  # Missing slot
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
            "recent_hospitalization": "recent_hospitalization",
            "current_lab_url": "current_lab_url",  # Missing slot
            "current_lab_username": "current_lab_username",  # Missing slot
            "current_lab_password": "current_lab_password",  # Missing slot
            "lab_credentials_status": "lab_credentials_status",  # Missing slot
        }

        # Check if user input matches any slot name
        if last_user_msg in slot_reset_map:
            slot_to_reset = slot_reset_map[last_user_msg]
            
            # Get current slot value to show what they previously answered
            current_value = tracker.get_slot(slot_to_reset)
            print(f"Current value for {slot_to_reset}: {current_value}")
            
            # Reset related slots based on dependencies
            slots_to_reset = [SlotSet(slot_to_reset, None)]
            
            # Handle smoking-related slot dependencies
            if slot_to_reset == "smoking_info":
                slots_to_reset.extend([
                    SlotSet("smoking_duration", None),
                    SlotSet("smoking_frequency", None)
                ])
            
            # Handle lab credentials dependencies
            if slot_to_reset == "imaging_lab_access":
                slots_to_reset.extend([
                    SlotSet("current_lab_url", None),
                    SlotSet("current_lab_username", None),
                    SlotSet("current_lab_password", None),
                    SlotSet("lab_credentials_status", None),
                    SlotSet("exam_passwords", None)
                ])
            
            # Create message with previous answer
            field_name = slot_to_reset.replace('_', ' ').title()
            if current_value:
                message = f"Your previous answer for {field_name} was: '{current_value}'\n\nI've reset this field. Let's fill it out again."
            else:
                message = f"I've reset the {field_name} field. Let's fill it out again."
            
            dispatcher.utter_message(text=message)
            
            return slots_to_reset + [
                ActiveLoop("medical_history_form"),
                FollowupAction("medical_history_form")
            ]
        else:
            # Create buttons for all correctable fields
            buttons = []
            for slot_name in slot_reset_map.keys():
                # Skip internal/technical slots from button display
                if slot_name not in ["smoking_duration", "smoking_frequency", "current_lab_url", 
                                   "current_lab_username", "current_lab_password", "lab_credentials_status"]:
                    buttons.append({
                        "title": slot_name.replace("_", " ").title(),
                        "payload": slot_name
                    })

            dispatcher.utter_message(
                text="Which field would you like to correct? Please choose one of the options below:",
                buttons=buttons
            )
            return []




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
                
                # Handle imaging_lab_access based on exam_passwords
                exam_passwords = data.get("exams_passwords") # this needs to be returned by db
                if exam_passwords and isinstance(exam_passwords, dict) and exam_passwords:
                    imaging_lab_access = "Yes"
                else:
                    imaging_lab_access = "No"
                
                # Map the JSON keys to your slot names
                slot_mapping = {
                    "chronic_disease": data.get("chronic_disease"),
                    "smoking_info": data.get("smoking"),
                    "medicine_info": data.get("medicines"),
                    # TODO add hospital_info to database
                    "hospital_info": data.get("hospital_history"),
                    "allergies_info": data.get("allergies"),
                    "hereditary_disease": data.get("existing_illness"),
                    "alcohol_info": data.get("alcohol_drug_use"),
                    # TODO add drug_use to database
                    "drug_use": data.get("drug_use"),
                    "sleep_diet": data.get("sleep_diet"),
                    "pregnancy_history": data.get("pregnancy_history"),
                    "recent_exams": data.get("recent_exams"),
                    "exam_passwords": exam_passwords,  # Store the exam passwords
                    "imaging_lab_access": imaging_lab_access,
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

    async def validate_imaging_lab_access(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate imaging_lab_access initial response."""
        
        # Handle both button payloads and direct text input
        if slot_value in ["yes", "no"] or tracker.latest_message.get('intent', {}).get('name') in ['affirm', 'deny']:
            # Map intent to text values
            if tracker.latest_message.get('intent', {}).get('name') == 'deny' or slot_value == "no":
                return {
                    "imaging_lab_access": "No",
                    "lab_credentials_status": "completed"
                }
            elif tracker.latest_message.get('intent', {}).get('name') == 'affirm' or slot_value == "yes":
                return {
                    "imaging_lab_access": "Yes",
                    "lab_credentials_status": "collecting"
                }
            else:
                # Handle direct text input
                if slot_value and slot_value.lower() in ['yes', 'y', 'true', '1']:
                    return {
                        "imaging_lab_access": "Yes",
                        "lab_credentials_status": "collecting"
                    }
                elif slot_value and slot_value.lower() in ['no', 'n', 'false', '0']:
                    return {
                        "imaging_lab_access": "No",
                        "lab_credentials_status": "completed"
                    }
                else:
                    dispatcher.utter_message(text="Please answer Yes or No.")
                    return {"imaging_lab_access": None}
        else:
            dispatcher.utter_message(text="Please select Yes or No.")
            return {"imaging_lab_access": None}

    async def validate_current_lab_url(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
            """Validate lab URL input."""
            
            if slot_value:
                # Basic URL validation
                if not slot_value.startswith(('http://', 'https://', 'www.')):
                    # Add protocol if missing
                    if not slot_value.startswith('www.'):
                        slot_value = 'www.' + slot_value
                    slot_value = 'https://' + slot_value
                
                return {"current_lab_url": slot_value}
            else:
                dispatcher.utter_message(text="Please enter a valid URL.")
                return {"current_lab_url": None}

    async def validate_current_lab_username(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate lab username input."""
        
        if slot_value and slot_value.strip():
            return {"current_lab_username": slot_value.strip()}
        else:
            dispatcher.utter_message(text="Please enter a valid username.")
            return {"current_lab_username": None}

    async def validate_current_lab_password(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate lab password input and store credentials."""
        
        if slot_value:
            current_credentials = tracker.get_slot("exam_passwords") or {}
            current_url = tracker.get_slot("current_lab_url")
            current_username = tracker.get_slot("current_lab_username")
            
            # Store credentials as a nested dictionary with URL as key
            current_credentials[current_url] = {
                "username": current_username,
                "password": slot_value
            }

            # After storing credentials, reset the status to trigger the "add more" question
            return {
                "current_lab_password": slot_value,
                "exam_passwords": current_credentials,
                "lab_credentials_status": None  # Reset to trigger the question
            }
        else:
            dispatcher.utter_message(text="Please enter a password.")
            return {"current_lab_password": None}
    async def validate_lab_credentials_status(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Interpret yes/no answer for adding more credentials."""
        
        intent = tracker.latest_message.get('intent', {}).get('name')

        if intent in ["affirm", "add_more_credentials"]:
            return {
                "lab_credentials_status": "collecting",
                "current_lab_url": None,
                "current_lab_username": None,
                "current_lab_password": None,
            }
        elif intent in ["deny", "done_adding_credentials"]:
            return {
                "lab_credentials_status": "completed"
            }

        # Fallback if text
        text = tracker.latest_message.get("text", "").lower()
        if any(w in text for w in ["yes", "add", "another", "more"]):
            return {
                "lab_credentials_status": "collecting",
                "current_lab_url": None,
                "current_lab_username": None,
                "current_lab_password": None,
            }
        elif any(w in text for w in ["no", "done", "finish", "complete"]):
            return {
                "lab_credentials_status": "completed"
            }

        dispatcher.utter_message(text="Please answer Yes or No.")
        return {"lab_credentials_status": None}


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

    async def next_slot_to_request(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Optional[Text]:
        """Determine the next slot to request based on conditional logic."""
        
        # Get current slot values
        lab_credentials_status = tracker.get_slot("lab_credentials_status")
        current_lab_url = tracker.get_slot("current_lab_url")
        current_lab_password = tracker.get_slot("current_lab_password")
        current_lab_username = tracker.get_slot("current_lab_username")
        imaging_lab_access = tracker.get_slot("imaging_lab_access")
        
        # Handle imaging lab credentials collection logic
        if imaging_lab_access == "Yes":
            # If we're collecting credentials or status is None (just finished collecting password)
            if lab_credentials_status == "collecting" or lab_credentials_status is None:
                if current_lab_url is None:
                    return "current_lab_url"
                elif current_lab_username is None:
                    return "current_lab_username"
                elif current_lab_password is None:
                    return "current_lab_password"
                elif lab_credentials_status is None:
                    # Just finished collecting password, ask if they want to add more
                    return "lab_credentials_status"
                else:
                    # Status is "collecting", ask if they want to add more
                    return "lab_credentials_status"
        
        # Get the standard next slot
        next_slot = await super().next_slot_to_request(dispatcher, tracker, domain)
        
        # If lab credentials are completed, skip credential-related slots
        if lab_credentials_status == "completed":
            if next_slot in ["current_lab_url","current_lab_username", "current_lab_password", "lab_credentials_status"]:
                # Move to the next main slot
                return "recent_hospitalization"
        
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
        """Return required slots based on conditions."""
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

        # Skip pregnancy history for males
        gender = tracker.get_slot("gender")
        if gender and gender.lower() in ["male", "m", "man"]:
            base_slots = [slot for slot in base_slots if slot != "pregnancy_history"]

        # Add credential collection slots only if user wants to share credentials
        imaging_lab_access = tracker.get_slot("imaging_lab_access")
        
        if imaging_lab_access == "Yes":
            try:
                imaging_index = base_slots.index("imaging_lab_access")
                base_slots.insert(imaging_index + 1, "current_lab_url")
                base_slots.insert(imaging_index + 2, "current_lab_username")
                base_slots.insert(imaging_index + 3, "current_lab_password")
                base_slots.insert(imaging_index + 4, "lab_credentials_status")
            except ValueError:
                pass

        return base_slots

    def get_exam_passwords(self, tracker: Tracker) -> Dict[str, str]:
        """
        Get the exam passwords dictionary.
        Use this method in your actions to get the credentials dictionary.
        """
        
        exam_passwords = tracker.get_slot("exam_passwords")
        
        if exam_passwords is None:
            return {}
        
        return exam_passwords if isinstance(exam_passwords, dict) else {}

    def format_credentials_for_storage(self, tracker: Tracker) -> Dict[str, Any]:
        """
        Format the credentials for final storage in your desired structure.
        Returns the complete structure with 'exams_passwords' key.
        """
        
        credentials_dict = self.get_exam_passwords(tracker)
        
        return {
            "exams_passwords": credentials_dict
        }



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
    
