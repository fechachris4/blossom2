from openai import OpenAI
import os
import logging

logging.basicConfig(
    filename="conversation.log",  # your log file
    filemode="a",                # append mode
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class LLM:
    def __init__(self, api_key, llm_prompt=None):
        """
        Initialize LLM class
        """
        # Set up OpenAI client using the provided API key
        self.client = OpenAI(api_key=api_key)
        
        # Use "gpt-4o" as model_id
        self.model_id = "gpt-4o"
        
        # Handle different prompt formats
        if llm_prompt is None:
            # Default prompt
            self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        elif isinstance(llm_prompt, list):
            # OpenAI message format (list of message dictionaries)
            self.conversation = []
            for msg in llm_prompt:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    self.conversation.append({
                        "role": msg["role"],
                        "content": str(msg["content"]).strip()
                    })
            # If no valid messages found, add default
            if not self.conversation:
                self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        elif isinstance(llm_prompt, dict):
            # Single message dictionary
            if "role" in llm_prompt and "content" in llm_prompt:
                self.conversation = [{
                    "role": llm_prompt["role"],
                    "content": str(llm_prompt["content"]).strip()
                }]
            else:
                self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]
        else:
            # String format - convert to system message
            prompt_text = str(llm_prompt).strip()
            if prompt_text:
                self.conversation = [{"role": "system", "content": prompt_text}]
            else:
                self.conversation = [{"role": "system", "content": "You are a helpful assistant."}]

    

    def request_response(self, text, role="user", addition_system_message=None):
        """
        Request response with current conversation context
        
        Parameters:
        - text: user input
        - role: "user" or "system"
        - addition_system_message: optional extra instruction to guide LLM behaviour
        
        Returns:
        - The content string from the LLM
        """
        # Validate input text
        if text is None or str(text).strip() == "":
            text = "Please respond."
        else:
            text = str(text).strip()
        
        # Add optional system message if provided
        if addition_system_message and str(addition_system_message).strip():
            self.conversation.append({
                "role": "system",
                "content": str(addition_system_message).strip()
            })
        
        # Add user/system message
        self.conversation.append({
            "role": role,
            "content": text
        })

        
        try:
            # Call the OpenAI API to get a response using the current conversation context
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=self.conversation
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            if response_text is None:
                response_text = "I apologize, but I couldn't generate a response."
            else:
                response_text = str(response_text).strip()
            
            # Add assistant response to conversation history
            self.conversation.append({
                "role": "assistant",
                "content": response_text
            })

            log_lines = ["\n" + "="*60]
            for i, msg in enumerate(self.conversation):
                log_lines.append(f"[{i}] {msg['role']}: {msg['content']}")
            log_lines.append("="*60)
            logger.info("\n".join(log_lines))
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            print(f"ERROR: {error_msg}")
            return "I apologize, but I encountered an error while processing your request."



        
