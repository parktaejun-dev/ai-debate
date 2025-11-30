import os
from abc import ABC, abstractmethod
import openai
import anthropic
import google.generativeai as genai

class DebateAgent(ABC):
    def __init__(self, name: str, role: str, api_key: str = None):
        self.name = name
        self.role = role
        self.api_key = api_key
        self.history = []

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def add_to_history(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

class OpenAIAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        self.client = openai.OpenAI(api_key=api_key)

    def generate_response(self, context: str) -> str:
        try:
            messages = [
                {"role": "system", "content": f"You are {self.name}. Your role is: {self.role}. Participate in the debate."}
            ]
            # Add context to messages (simplified for now, ideally we parse the context)
            messages.append({"role": "user", "content": context})

            response = self.client.chat.completions.create(
                model="gpt-4o", # Using a capable model
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class AnthropicAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(self, context: str) -> str:
        try:
            system_prompt = f"You are {self.name}. Your role is: {self.role}. Participate in the debate."
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"

class GoogleGeminiAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_response(self, context: str) -> str:
        try:
            prompt = f"System: You are {self.name}. Your role is: {self.role}. Participate in the debate.\n\nContext:\n{context}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

class MockAgent(DebateAgent):
    def generate_response(self, context: str) -> str:
        return f"[{self.name} Mock Response] I agree/disagree with the previous point about advertising because..."
