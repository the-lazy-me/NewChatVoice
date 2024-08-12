from graiax import silkcoder


def convert_to_silk(mp3_path: str) -> str:
    silk_path = mp3_path.replace('.mp3', '.silk')
    silkcoder.encode(mp3_path, silk_path)
    return silk_path
