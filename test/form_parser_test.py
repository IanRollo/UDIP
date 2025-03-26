import unittest
import os

from src.document_reconstructor import DocumentReconstructor
from src.form_parser import FormParser

azure_key = os.environ.get("AZURE_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")

class FormParserTest(unittest.TestCase):
    def runTest(self):
        form_parser = FormParser(azure_key, './working')
        document_reconstructor = DocumentReconstructor('./config')
        form_parser.parse(document_reconstructor)
        # self.assertEqual(True, False)  # add assertion here
        # TODO: once we have consistent test cases, use the same thing every time and assert that the contents of the
        #  CSV are correct

    def compare(self):
        # Parse the 'removed_inputs' inputs using each type of parser
        # Measure the number of tokens for each one
        # Measure the number of errors for each one
        # Print the number of tokens, num errors, and ratio of tokens to % correct
        pass


if __name__ == '__main__':
    unittest.main()
