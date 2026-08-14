from abc import ABC, abstractmethod
from app.services.ai.classifier import Classification

class AIProvider(ABC):
    name: str
    @abstractmethod
    async def classify(self,text:str,allowed_categories:list[str])->Classification: ...
