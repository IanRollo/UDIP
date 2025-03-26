import os
from os import path
from openai import OpenAI
from azure.ai.formrecognizer import AnalyzeResult
from pydantic import BaseModel

from src.utils import read_from_file, write_to_file

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

def create_blank_canvas(width, height):
    """
    Create a blank canvas using page width and height
    """
    return [[' ' for _ in range(int(width))] for _ in range(int(height))]


def add_word_to_canvas(canvas, word, polygon):
    """
    Add a word to an existing canvas based on its coordinates
    """
    min_x = min(point.x for point in polygon)
    min_y = min(point.y for point in polygon)
    word_with_space = word + ' '  # Add a space after the word
    for i, char in enumerate(word_with_space):
        if (int(min_x) + i) < len(
                canvas[int(min_y)]):  # Check if the index is within the canvas width
            canvas[int(min_y)][int(min_x) + i] = char


def reconstruct_document(result: AnalyzeResult, output_file_name: str):
    with open(output_file_name, "w", encoding='utf-8') as output_file:
        first_page = result.pages[0]
        canvas = create_blank_canvas(first_page.width, first_page.height)
        for word in first_page.words:
            word_content, polygon = word.content, word.polygon
            add_word_to_canvas(canvas, word_content, polygon)

        for row in canvas:
            row_string = "".join(column for column in row)
            output_file.write(row_string + "\n")
        output_file.close()
    # return read_from_file(output_file_name)


def replace_spaces_with_tab(input_file_name, output_file_name):
    with open(input_file_name, 'r') as in_file, open(output_file_name, 'w') as output_file:
        for line in in_file:
            # # Remove leading and trailing spaces
            # line = line.strip()
            # Skip empty lines
            if not line:
                continue
            # Replace four spaces with a tab and write the line to the output file
            output_file.write(line.replace('    ', '\t') + '\n')
        output_file.close()

# The reconstructed document method is no longer efficient, and is deprecated, leaving for now in case it becomes efficient again.
def generate_debug_file(analyze_result: AnalyzeResult, debug_dir: str) -> str:
    reconstructed_filepath = path.join(debug_dir, 'reconstructed_file.txt')
    tab_reconstructed_filepath = path.join(debug_dir, 'tab_reconstructed_file.txt')
    reconstruct_document(analyze_result, reconstructed_filepath)
    replace_spaces_with_tab(reconstructed_filepath, tab_reconstructed_filepath)
    return read_from_file(tab_reconstructed_filepath)

def generate_word_poly_debug_file(analyze_result) -> str:
    output_lines = []
    # Iterate over each paragraph in the result
    for paragraph in analyze_result.paragraphs:
        # Make sure there is at least one bounding region and polygon
        if paragraph.bounding_regions and paragraph.bounding_regions[0].polygon:
            polygon_point = paragraph.bounding_regions[0].polygon[0]
            point_str = f"{polygon_point.x} {polygon_point.y}"
            output_lines.append(f"{paragraph.content} {point_str}")
    return "\n".join(output_lines)

class PatientData(BaseModel):
    Document_Type: str
    Patient_First_Name: str
    Patient_Last_Name: str
    Patient_ID: str
    Patient_Email: str
    Patient_Phone_Number: str


patient_schema_dict = PatientData.model_json_schema()
class DocumentReconstructor:

    def __init__(self, config_dir: str):
        """
        :param api_key: the API key for OpenAI's ChatGPT
        :param config_dir: a directory containing configurations. Config files must be named "example.txt",
               "example_response.txt", "operating_parameters.txt", and "prompt.txt".
        """
        self.example_response = read_from_file(path.join(config_dir, 'example_response.txt'))
        self.example = read_from_file(path.join(config_dir, 'example.txt'))
        self.op_params = read_from_file(path.join(config_dir, 'operating_parameters.txt'))
        self.prompt_str = read_from_file(path.join(config_dir, 'prompt.txt'))



    def parse(self, filename: str, analyze_result: AnalyzeResult, debug_dir: str):
        debug_content = generate_word_poly_debug_file(analyze_result)
        debug_filepath = path.join(debug_dir, filename.replace(".", "-") + ".txt")
        write_to_file(debug_content, debug_filepath)
        client = OpenAI(
            api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
        )
        prompt = self.prompt_str + debug_content
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
                            "text": prompt,
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
                        patient_schema_dict
                }
            },
            # Ensure that PatientData is defined correctly or replace with the appropriate value
        )
        return output
