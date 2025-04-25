# Form Parser

This form-parsing program takes in a folder full of images of forms, processes them, and writes the contents of all of the forms into a single JSON.

## Setup & Use

The form parser requires Python version 3.9 or later. You can install Python [here](https://www.python.org/downloads/).

### PyCharm

During development, we've been running the form parser within PyCharm. To run the project this way, do the following:

1. Download PyCharm, if you don't already have it. The community edition can be downloaded for free.
2. Clone this repository and navigate into the project directory.
   ```bash
   $ cd UDIP
   ```
3. Open the project folder (`UDIP`) in PyCharm.
3. Move your input files into the `/test/working/inputs` directory. Some are already available to mess around with.
4. Run the unit test. Outputs will be visible in the `/test/working/outputs` directory.

### Command Line

1. Clone this repository and navigate into the project directory.
   ```bash
   $ cd UDIP
   ```
2. Install the requirements. [Pip](https://pypi.org/project/pip/) is the most common package installer for Python; if you don't have it, you can download it at the linked page. Once you have pip installed, you can run this command to install the requirements for the form parser:
   ```bash
   $ pip install -r requirements.txt
   ```
3. Put the images of the forms you want to parse into a folder.
4. Create a folder to store the debug output in. If you don't know what that is, don't worry about it; just create an empty folder.
5. Create a folder to put the final JSON output in.
6. Get an [Azure](https://azure.microsoft.com/en-us) API key, a FormRecognizer endpoint, and an [OpenAI](https://openai.com/) API key. You will need to build a FormRecognizer instance in Azure to get this.
7. Run the parser from the command line using the inputs you gathered in steps 3-6:
   ```bash
   $ python src/form_parser.py \
     --azure_api_key <the API key for Azure, from step 6> \
     --openai-api-key <the API key from OpenAI, from step 6> \
     --prompt_filepath "test/prompt.txt" \
     --example_filepath "test/example.txt" \
     --input_dir <the path to the folder from step 3> \
     --debug_dir <the path to the folder from step 4> \
     --output_dir <the path to the folder from step 5>
   ```
8. When the command line returns, check the `output_dir` folder from step 5. It should now contain a file called `output.csv` with the parsed contents of your forms.

## Reading the Output

The CSV file will be formatted as described in the `prompt.txt` file.
