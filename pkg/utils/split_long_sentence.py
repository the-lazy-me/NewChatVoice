import re
from typing import List

def split_long_sentence(text: str, max_length: int) -> List[str]:
    text = re.sub(r'\n+', '\n', text).strip()
    paragraphs = text.split('\n')
    short_sentences = []

    for paragraph in paragraphs:
        if len(paragraph) <= max_length:
            short_sentences.append(paragraph)
        else:
            sentences = re.split(r"(?<=[。！？；：.!?;:])", paragraph)
            current_sentence = ""
            for sentence in sentences:
                if len(current_sentence) + len(sentence) > max_length:
                    if current_sentence:
                        short_sentences.append(current_sentence)
                    current_sentence = sentence
                else:
                    current_sentence += sentence
            if current_sentence:
                short_sentences.append(current_sentence)

    return short_sentences
