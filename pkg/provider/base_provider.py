from abc import ABC, abstractmethod


class TTSInterface(ABC):
    @abstractmethod
    async def get_character_list(self, file_path: str = None):
        pass

    @abstractmethod
    async def generate_audio(self, text: str, character_id: int, **kwargs):
        pass