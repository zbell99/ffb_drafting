from abc import ABC, abstractmethod

class PayloadProcessor(ABC):
    @abstractmethod
    def process(self, draft_id: str) -> dict:
        pass