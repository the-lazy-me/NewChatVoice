from .acgn_ttson import ACGNTTSon
from .gpt_sovits import GPTSovits


class ProviderFactory:
    @staticmethod
    def get_provider(provider_name, config, temp_dir_path):
        if provider_name == "acgn_ttson":
            provider = ACGNTTSon(temp_dir_path)
            provider.set_token(config["token"])
            return provider
        elif provider_name == "gpt_sovits":
            return GPTSovits(config["url"], temp_dir_path)
        else:
            raise ValueError(f"未知的TTS平台: {provider_name}")
