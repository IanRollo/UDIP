import os
from os import path
from openai import OpenAI
from azure.ai.formrecognizer import AnalyzeResult
from pydantic import BaseModel

from src.utils import read_from_file, write_to_file, generate_base_debug_file


#Converts to a dict to enable it to work with GPT

class DocumentReconstructor:

    def __init__(self, config_dir: str):
        """
        :param config_dir: a directory containing configurations. Config files must be named "example.txt",
               "example_response.txt", "operating_parameters.txt", and "prompt.txt".
        """
        self.example_response = read_from_file(path.join(config_dir, 'example_response.txt'))
        self.example = read_from_file(path.join(config_dir, 'example.txt'))
        self.op_params = read_from_file(path.join(config_dir, 'operating_parameters.txt'))
        self.prompt_str = read_from_file(path.join(config_dir, 'prompt.txt'))
        self.patient_schema_dict = self.PatientData.model_json_schema()

    class PatientData(BaseModel):
        Document_Type: str
        Patient_First_Name: str
        Patient_Last_Name: str
        Patient_ID: str
        Patient_Email: str
        Patient_Phone_Number: str


    def parse(self, filename: str, analyze_result: AnalyzeResult, debug_dir: str):
        debug_content = generate_base_debug_file(analyze_result)
        debug_filepath = path.join(debug_dir, filename.replace(".", "-") + ".txt")
        write_to_file(debug_content, debug_filepath)
        client = OpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
        )
        prompt = debug_content
        output = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self.op_params,
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "patient_data",
                    "strict": False,
                    "schema":
                        self.patient_schema_dict
                }
            },
            # Ensure that PatientData is defined correctly or replace with the appropriate value
        )
        return output
