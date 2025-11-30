import os
from abc import ABC, abstractmethod
import openai
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

class DeepSeekAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def generate_response(self, context: str) -> str:
        try:
            messages = [
                {"role": "system", "content": f"You are {self.name}. Your role is: {self.role}. Participate in the debate. IMPORTANT: You must answer in Korean."}
            ]
            messages.append({"role": "user", "content": context + "\n\n(한국어로 답변해주세요)"})

            response = self.client.chat.completions.create(
                model="deepseek-chat", 
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class PerplexityAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )

    def generate_response(self, context: str) -> str:
        try:
            messages = [
                {"role": "system", "content": f"You are {self.name}. Your role is: {self.role}. Participate in the debate. IMPORTANT: You must answer in Korean."}
            ]
            messages.append({"role": "user", "content": context + "\n\n(한국어로 답변해주세요)"})

            response = self.client.chat.completions.create(
                model="llama-3.1-sonar-large-128k-online", 
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class GoogleGeminiAgent(DebateAgent):
    def __init__(self, name: str, role: str, api_key: str):
        super().__init__(name, role, api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def generate_response(self, context: str) -> str:
        try:
            prompt = f"System: You are {self.name}. Your role is: {self.role}. Participate in the debate. IMPORTANT: You must answer in Korean.\n\nContext:\n{context}\n\n(한국어로 답변해주세요)"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

class MockAgent(DebateAgent):
    def generate_response(self, context: str) -> str:
        return f"[{self.name} Mock Response] (한국어로 답변) 광고의 미래에 대해 동의/반대합니다. 왜냐하면..."
