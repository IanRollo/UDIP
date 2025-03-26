from os import path
from typing import TextIO, List

import tiktoken
from azure.ai.formrecognizer import DocumentParagraph, AnalyzeResult


def open_file(filepath: str) -> TextIO:
    """
    Opens a file for writing at the specified filepath. If the file does not exist, it creates it.
    If the file already exists and there's something in it already, whatever is in it already will be removed.
    :param filepath: the path of the file to open
    :return: a text IO stream (don't forget to close it when you're done)!
    """
    if not path.exists(filepath):
        open(filepath, "x").close()  # create the file if it doesn't already exist
    return open(filepath, "w")  # open the file for writing, clearing whatever was already in it


def read_from_file(filepath: str) -> str:
    """
    Helper function to quickly get the text from a .txt file. Opens the file, reads it, closes it,
    and returns its contents as a string.
    :param filepath: the path of the file to get the text from
    :return: a string whose content is the text in the file
    """
    with open(filepath, "r") as opened_file:
        result = "\n".join(opened_file.readlines())
        opened_file.close()
    return result


def write_to_file(content, output_file_name):
    with open(output_file_name, "w") as output_file:
        output_file.write(str(content))
        output_file.close()


def filter_role(paragraphs: List[DocumentParagraph], role: str) -> List[DocumentParagraph]:
    """Given a list of Azure DocumentParagraphs, return a list of only the ones that have the specified role."""
    return list(filter(lambda paragraph: paragraph.role == role, paragraphs))


def extract_title(result: AnalyzeResult) -> str or None:
    """
    Find the title of an Azure AnalyzeResult, if it exists, by searching for "title" and "subtitle" roles.
    :param result: the AnalyzeResult whose title we're looking for
    :return: the title if it is found, or None if it is not found
    """
    paragraphs = result.paragraphs
    title_paragraphs = filter_role(paragraphs, "title")
    if len(title_paragraphs) > 0:
        return title_paragraphs[0].content
    else:
        title_paragraphs = filter_role(paragraphs, "subtitle")
        if len(title_paragraphs) > 0:
            return title_paragraphs[0].content
    return None


def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}. See 
        https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to 
        tokens.""")