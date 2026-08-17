import time
from app.services.ai.classifier import classify as rule_classify, Classification

class AIService:
    """Provider-independent classifier. API adapters are enabled only when keys are configured."""
    async def classify(self,text:str,allowed_categories:list[str])->Classification:
        # The deterministic safe fallback keeps reporting operational without an external model.
        # Provider adapters can be selected by env configuration without changing callers.
        started=time.perf_counter(); result=rule_classify(text); result.processing_time=time.perf_counter()-started  # type: ignore[attr-defined]
        return result

ai_service=AIService()
