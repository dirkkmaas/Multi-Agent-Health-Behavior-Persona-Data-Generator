import json

class ConversationHandler:
    """"Runs conversation with the experts, adds episodic memories and semantic memories to the prompt for the expert. Finally it uses a reflection
    template to update the episodic memory."""
    def __init__(self, prompt_manager, agent, collection_episodic: str, collection_semantic: str, top_k_episodic: int, top_k_semantic: int, name: str):
        self.prompt_manager = prompt_manager
        self.agent = agent
        self.collection_episodic = collection_episodic
        self.collection_semantic = collection_semantic
        self.top_k_episodic = top_k_episodic
        self.top_k_semantic = top_k_semantic
        self.messages = []
        self.name=name

    def format_conversation(self, messages):
        """"Create conversation summary for the episodic memory """
        conversation = []
        for message in messages:
            if message['role'] in ['assistant', 'user']:
                conversation.append(f"{message['role'].capitalize()}: {message['content']}")
        return "\n".join(conversation)

    def run_conversation(self,prompt):
        """'Runs the conversation with the user"""
        user_message = {"role": "user", "content": prompt}
        if prompt.lower() == "exit":
            if self.messages == []: # ensure that there are messages to reflect on
                return json.dumps({
                    "prompt": {"message_id": "warning", "expert_prompt": "Please interact with the agent first before updating memory."},
                    "response": {"last_message": "No messages to store. Please have a conversation with the agent first."}
                })
            else:
                from core import ConversationReflection
                from memory import ChromaMemory
                memory = ChromaMemory()
                reflection_generator = ConversationReflection(self.agent, self.prompt_manager.reflection_prompt_file)
                conversation = self.format_conversation(self.messages)
                reflection = reflection_generator.reflect_on_conversation(conversation)
                memory.add_entry(reflection, self.collection_episodic)
                # Clear messages after storing in episodic memory
                self.messages = []
                return json.dumps({
                    "prompt": {"message_id": "success", "expert_prompt": "Memory updated successfully."},
                    "response": {"last_message": "Memory has been updated and conversation history cleared."}
                }) # send if update succesfull
        self.messages.append(user_message) # add user message
        system_prompt = self.prompt_manager.get_episodic_prompt(prompt, self.collection_episodic, self.top_k_episodic) #enhance prompt with episodic knowledge
        system_message = {"role": "system", "content": system_prompt.content} # set system prompt
        self.messages = [system_message] + [msg for msg in self.messages if msg["role"] != "system"] # add all messages except system prompt
        context_message = self.prompt_manager.get_semantic_prompt(prompt, self.collection_semantic, self.top_k_semantic) # get semantic knowledge if availabe
        combined_string = (
                "#### Episodic Memory:\n\n" +
                json.dumps(self.messages, ensure_ascii=False, indent=2) +
                "\n\n---\n\n#### Semantic Memory:\n" +
                context_message
            )# create string for placeholder message to show in streamlit
        placeholder = [*self.messages, context_message, user_message]
        response = self.agent.query(placeholder)
        message_id = response.id # get response id
        prompt_id={"message_id": message_id, "expert_prompt": combined_string} # to log the prompt in the expert message
        content = response.content # content of response
        self.messages.append({"role": "assistant", "content": content}) 
        final_response={"last_message": content} # final response
        end_message = json.dumps({
            "prompt": prompt_id,
            "response": final_response
        }) # prompt and response        
        return end_message
