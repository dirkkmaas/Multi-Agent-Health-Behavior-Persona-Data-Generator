from core import ConversationHandler, PromptManager

class AgentBuilder:
    """"Class to build an agent, with all the required input"""
    def __init__(self, system_prompt_file: str, episodic_prompt_file: str, semantic_prompt_file: str, 
                reflection_prompt_file: str, episodic_collection: str, semantic_collection: str, episodic_number: int, semantic_number: int,  agent, agent_name:str):
        self.prompt_manager = PromptManager(system_prompt_file, episodic_prompt_file, semantic_prompt_file, reflection_prompt_file)
        self.llm_agent = agent
        self.conversation_handler = ConversationHandler(self.prompt_manager, self.llm_agent, episodic_collection, semantic_collection,episodic_number,semantic_number,agent_name)
    
    def run(self,prompt):
        response=self.conversation_handler.run_conversation(prompt)
        return response
