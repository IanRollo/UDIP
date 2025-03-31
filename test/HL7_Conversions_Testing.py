import json
import os
from datetime import datetime
import argparse
class MessageConversions:

    # HL7 message creation
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

    def convert_and_write_hl7_from_json(working_dir):
        input_path = os.path.join(working_dir, "output", "output.json")
        output_path = os.path.join(working_dir, "output", "patient_message.HL7")

        with open(input_path, "r") as f:
                data = json.load(f)

        hl7_input = data[0]["output"][0]["content"][0]["text"]
        patient_data = json.loads(hl7_input)

        hl7_message = MessageConversions.json_to_hl7(patient_data)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(hl7_message)

        print(f"HL7 message written to {output_path}")

def main():
    parser = argparse.ArgumentParser(
            description="Converts patient data in output.json to HL7 format and writes it to output directory"
         )
    parser.add_argument('-a', '--azure_api_key')
    parser.add_argument('-c', '--config_dir')
    parser.add_argument('-w', '--working_dir')

    args = parser.parse_args()

    MessageConversions.convert_and_write_hl7_from_json(args.working_dir)

if __name__ == "__main__":
    main()