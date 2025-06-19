from langchain_core.messages import SystemMessage
import os



class PromptManager:
    """Determines how the prompt of the expert is updated, based on the availability of data in the episodic and semantic memory. 
    Load the different specified prompt templates from the set_up file"""
    def __init__(self, system_prompt_file: str, episodic_prompt_file: str, semantic_prompt_file: str, reflection_prompt_file: str):
        """
        Initialize the PromptManager by loading system, episodic, and semantic prompt from text files.
        """
        self.system_prompt = self._load_prompt_from_file(system_prompt_file)
        self.episodic_prompt_template = self._load_prompt_from_file(episodic_prompt_file)
        self.semantic_prompt_template = self._load_prompt_from_file(semantic_prompt_file)
        self.reflection_prompt_file = reflection_prompt_file
        
        
    def _load_prompt_from_file(self, file_path: str):
        """Loads the contents of a text file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        with open(file_path, 'r') as file:
            return file.read().strip()

    def get_episodic_prompt(self, query: str, collection: str, top_k : int):
        """Generate the episodic prompt using the template and query."""
        from memory import ChromaMemory
        database = ChromaMemory()
        memory = database.search(query, collection, top_k)
        if not memory or memory == ["No results found."]:
            return SystemMessage(content=self.system_prompt)
        conversations = []
        what_worked = set()
        what_to_avoid = set()
        conversation_history = set()

        for result in memory:
            conversation_history.update(result.get("conversation_summary", "").split('. ') if result.get("conversation_summary") else [])
            what_worked.update(result.get("what_worked", "").split('. ') if result.get("what_worked") else [])
            what_to_avoid.update(result.get("what_to_avoid", "").split('. ') if result.get("what_to_avoid") else [])
        #all the format parts have to change based on the episodic prompt file, goal is to make it universally changeable 
        episodic_prompt = f"{self.system_prompt}\n\n" + self.episodic_prompt_template.format(
            conversation_history=' '.join(conversation_history) if conversation_history else "No insights yet.",
            what_worked=' '.join(what_worked) if what_worked else "No insights yet.",
            what_to_avoid=' '.join(what_to_avoid) if what_to_avoid else "No specific avoidance rules."
        ) # add system prompt with new history of what worked, what to avoid and conversation summary
        
        return SystemMessage(episodic_prompt)

    def get_semantic_prompt(self, query: str, collection: str, top_k :int):
        """Generate the semantic prompt using the template and query."""
        from memory import ChromaMemory
        database = ChromaMemory()
        memories = database.search(query, collection, top_k)

        semantic_prompt = self.semantic_prompt_template.format(memories=memories) # memories as entry
        
        return semantic_prompt
