from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from os import listdir, path


# use your `key` and `endpoint` environment variables
key = 'aa31f6448f3a40018823eaab9ef80e45'
endpoint = 'https://roformrecognizer1.cognitiveservices.azure.com/'


# sample form document
input_dir = r'C:\Users\ianys\PycharmProjects\ChatGPT4IR\test\working\inputs'
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

for file in [f for f in listdir(input_dir) if path.isfile(path.join(input_dir, f))]:
    # parse the file into a result with keys & values in Azure
    input_filepath = path.join(input_dir, file)
    with open(input_filepath, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document=f
        )
    result = poller.result()
    first_page = result.pages[0]

    for word in first_page.words:
        print(word.content)


