from googletrans import Translator

translator = Translator()

# 中文國名,
chinese_names = ['台灣', '日本', '德國', '法國', '中華台北', '韓國']

# 翻譯中文國名為英文,
translated_names = [translator.translate(name, src='zh-TW', dest='en').text for name in chinese_names]

# 修正翻譯結果
translated_names = [
    "Chinese Taipei" if name == "Taiwan" else
    "Korea" if name == "South Korea" else
    name
    for name in translated_names
]

print("翻譯成英文：", translated_names)