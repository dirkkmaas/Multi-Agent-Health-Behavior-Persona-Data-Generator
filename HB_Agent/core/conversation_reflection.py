from langchain.prompts import ChatPromptTemplate
import os
from langchain_core.output_parsers.json import JsonOutputParser


class ConversationReflection:
    """Create the reflection from the message to update the episodic memory."""
    def __init__(self, llm, reflection_prompt_file: str):
        self.llm = llm
        self.reflection_prompt_template = self._load_prompt_from_file(reflection_prompt_file)
        self.reflection_prompt_file = ChatPromptTemplate.from_template(self.reflection_prompt_template)

    def _load_prompt_from_file(self, file_path: str):
        """Loads the contents of a text file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        with open(file_path, 'r') as file:
            return file.read().strip()

    def reflect_on_conversation(self, conversation: str):
        prompt = self.reflection_prompt_file.format(conversation=conversation)
        response = self.llm.query(prompt)
        message = response.content
        parsed_response = JsonOutputParser().parse(message)
        return parsed_response

