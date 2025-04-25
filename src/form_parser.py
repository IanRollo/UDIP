"""
Reads a folder full of PDFs and uses Azure + ChatGPT to output them all to a single CSV.
TODO: refactor into separate classes later.

Steps:
1. Take in a file from the input directory
2. Upload it to Azure
3. Parse it into keys & values using Azure
4. Export the keys & values to a .txt file in the debug directory
5. Use ChatGPT to parse the keys & values from the .txt file into a CSV row
6. Write the row to the in-progress output CSV
7. Once all files are processed, copy the output CSV into a target directory
"""
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult
from os import path, listdir, getenv
import json
from src.document_reconstructor import DocumentReconstructor
import argparse
from src.post_output_conversions import MessageConversions

ENDPOINT = getenv('FORMRECOGNIZER_ENDPOINT')
if not ENDPOINT:
    raise EnvironmentError("FORMRECOGNIZER_ENDPOINT environment variable not set.")


class FormParser:

    def __init__(self, azure_api_key: str, working_dir: str):
        """
        :param azure_api_key: the API key for Microsoft Azure's Form Recognizer
        :param working_dir: a directory containing three other directories. These directories must be named "debug",
               "input", and "output". The "debug" and "output" subdirectories should be empty; the "input" directory should
               contain the images that need to be parsed as forms.
        """
        self.debug_dir = path.join(working_dir, 'debug')
        self.input_dir = path.join(working_dir, 'input')
        self.output_dir = path.join(working_dir, 'output')
        self.analysis_client = DocumentAnalysisClient(
            endpoint=ENDPOINT, credential=AzureKeyCredential(azure_api_key)
        )

    def analyze_document(self, input_filepath: str) -> AnalyzeResult:
        with open(input_filepath, "rb") as f:
            poller = self.analysis_client.begin_analyze_document(
                "prebuilt-read", document=f
            )
        return poller.result()

    def parse(self, result_analyzer) -> None:
        aggregated_results = []  # list to hold JSON responses from each file

        # Iterate through each file in the input directory
        for file in [f for f in listdir(self.input_dir) if path.isfile(path.join(self.input_dir, f))]:
            input_filepath = path.join(self.input_dir, file)
            result = self.analyze_document(input_filepath)

            # Get the response from your analyzer.
            # It might be a string, a dict, or a pydantic model.
            json_response = result_analyzer.parse(file, result, self.debug_dir)

            # Determine the type and convert accordingly:
            if isinstance(json_response, str):
                try:
                    parsed_response = json.loads(json_response)
                except Exception as e:
                    print(f"Error parsing JSON string for file {file}: {e}")
                    parsed_response = json_response
            elif isinstance(json_response, dict):
                parsed_response = json_response
            elif hasattr(json_response, "model_dump"):
                parsed_response = json_response.model_dump()
            else:
                parsed_response = json_response

            aggregated_results.append(parsed_response)
            print(parsed_response)

        # Write the aggregated JSON responses to a file in the output directory
        output_file_path = path.join(self.output_dir, 'output.json')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            json.dump(aggregated_results, output_file, indent=2)


def main():
    parser = argparse.ArgumentParser(
        prog='form_parser',
        description='Reads a folder full of images of forms and output the contents of all the forms to a single CSV.'
    )
    parser.add_argument('-a', '--azure_api_key')
    parser.add_argument('-c', '--config_dir')
    parser.add_argument('-w', '--working_dir')

    args = parser.parse_args()

    document_reconstructor = DocumentReconstructor(args.config_dir)
    form_parser = FormParser(args.azure_api_key, args.working_dir)
    form_parser.parse(document_reconstructor)
    hl7_converter = MessageConversions(args.working_dir)
    hl7_converter.convert_and_write_hl7_from_json()