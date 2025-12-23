# app/services/llm/base.py
from abc import ABC, abstractmethod

class BaseLLM(ABC):

    @abstractmethod
    async def generate_system_design(self, prompt: str):
        pass

    @abstractmethod
    async def generate_component_tree(self, prompt: str):
        pass
