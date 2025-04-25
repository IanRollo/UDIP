import json
import os
from datetime import datetime
from os import path
class MessageConversions:
    def __init__(self, working_dir: str):
        self.output_dir = path.join(working_dir, "output")

    # HL7 message creation
    @staticmethod
    def json_to_hl7(patient_data):
        # HL7 delimiters
        field_sep = '|'
        comp_sep = '^'
        rep_sep = '~'
        esc_char = '\\'
        subcomp_sep = '&'

        # MSH Segment
        sending_app = "App"
        sending_fac = "Clinic"
        receiving_app = "HospitalSys"
        receiving_fac = "MainHospital"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        message_type = "ADT^A04"
        message_control_id = "12345"
        hl7_version = "2.3"

        msh = f"MSH{field_sep}^~\\&{field_sep}{sending_app}{field_sep}{sending_fac}{field_sep}{receiving_app}{field_sep}{receiving_fac}{field_sep}{timestamp}{field_sep}{field_sep}{message_type}{field_sep}{message_control_id}{field_sep}P{field_sep}{hl7_version}"

        # PID Segment
        pid = f"PID{field_sep}1{field_sep}{field_sep}{patient_data['Patient_ID']}{field_sep}{field_sep}{patient_data['Patient_Last_Name']}{comp_sep}{patient_data['Patient_First_Name']}{field_sep}{field_sep}{field_sep}{field_sep}{field_sep}{patient_data['Patient_Phone_Number']}"

        return f"{msh}\n{pid}"

    def convert_and_write_hl7_from_json(self):
        input_path = path.join(self.output_dir, "output.json")
        output_path = path.join(self.output_dir, "patient_message.HL7")

        with open(input_path, "r") as f:
            data = json.load(f)

        hl7_messages = []

        for entry in data:
            try:
                hl7_input = entry["output"][0]["content"][0]["text"]
                patient_data = json.loads(hl7_input)
                hl7_message = MessageConversions.json_to_hl7(patient_data)
                hl7_messages.append(hl7_message)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"Warning: Could not process entry: {e}")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write("\n\n".join(hl7_messages))  # Add a double line break between messages

        print(f"{len(hl7_messages)} HL7 messages written to {output_path}")