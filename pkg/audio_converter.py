from graiax import silkcoder


# def convert_to_silk(wav_path: str, temp_folder: str) -> str:
#     silk_path = os.path.join(temp_folder, Path(wav_path).stem + '.silk')
#     silkcoder.encode(wav_path, silk_path)
#
#     # print(f"已将 WAV 文件 {wav_path} 转换为 SILK 文件 {silk_path}")
#     return silk_path

# MP3转换为silk，参数为MP3文件路径，返回silk文件路径
def convert_to_silk(mp3_path: str) -> str:
    silk_path = mp3_path.replace('.mp3', '.silk')
    silkcoder.encode(mp3_path, silk_path)
    return silk_path