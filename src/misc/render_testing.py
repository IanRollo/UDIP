import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from os import listdir, path


# use your `key` and `endpoint` environment variables
key = 'aa31f6448f3a40018823eaab9ef80e45'
endpoint = 'https://roformrecognizer1.cognitiveservices.azure.com/'

# sample form document
input_dir = r'C:\Users\ianys\PycharmProjects\ChatGPT4IR\test\working\inputs'
output_file_name = r'C:\Users\ianys\PycharmProjects\ChatGPT4IR\test\working\outputs\wordpoly.txt'
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)


def __main__():
    for file in [f for f in listdir(input_dir) if path.isfile(path.join(input_dir, f))]:
        # parse the file into a result with keys & values in Azure
        input_filepath = path.join(input_dir, file)
        with open(input_filepath, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-read", document=f
            )
        result = poller.result()

        # for paragraph in result.paragraphs:
        #     print(paragraph.content)

        with open(output_file_name, "w") as output_file:
            for paragraph in result.paragraphs:
                paragraph_content, polygon1 = paragraph.content, paragraph.bounding_regions[0].polygon[0]
                point_str = "{0} {1}".format(polygon1.x, polygon1.y)
                print(paragraph_content, point_str)
                output_line = "{} {}".format(paragraph_content, point_str)
                output_file.write(output_line + "\n")
