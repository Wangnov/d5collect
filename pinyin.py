import json
from pypinyin import pinyin, Style
from collections import defaultdict

# 处理拼音
"""将所有汉字转换为拼音，支持多音字"""
with open('costumes_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# 收集所有汉字字符
character_list = []
for i in d:
    idx = 0
    while idx < len(i['name']):
        if i['name'][idx].isalpha():
            character_list.append(i['name'][idx].lower())
            break
        idx += 1

# 去重
character_list = list(set(character_list))

# 构建多音字拼音字典：拼音 -> [字符列表]
pinyin_to_chars = defaultdict(set)
char_to_pinyins = {}  # 字符 -> [拼音列表]

# 为每个字符获取所有可能的拼音（支持多音字）
for char in character_list:
    # 获取该字符的所有拼音读音
    char_pinyins = pinyin(char, heteronym=True, style=Style.NORMAL)[0]
    char_to_pinyins[char] = char_pinyins
    
    # 建立拼音到字符的反向映射
    for py in char_pinyins:
        pinyin_to_chars[py].add(char)

# 将set转换为list以便后续使用
pinyin_to_chars = {py: list(chars) for py, chars in pinyin_to_chars.items()}

def get_matching_costumes(input_str):
    """
    获取输入字符串中每个汉字对应的读音相同的costume内容列表（支持多音字）
    :param input_str: 用户输入的汉字字符串
    :return: 按输入顺序排列的每个汉字对应的costume内容列表（嵌套列表形式）
    """
    input_str = input_str.lower()  # 转换为小写以支持大小写不敏感匹配
    result = []
    
    for char in input_str:
        matching_costumes = []
        
        # 获取输入字符的所有可能拼音
        if char in char_to_pinyins:
            input_char_pinyins = char_to_pinyins[char]
        else:
            # 如果字符不在预处理的字典中，动态获取其拼音
            try:
                input_char_pinyins = pinyin(char, heteronym=True, style=Style.NORMAL)[0]
            except Exception:
                input_char_pinyins = []
        
        # 对于输入字符的每个拼音，查找所有匹配的costume
        matched_items = set()  # 使用set避免重复
        
        for input_pinyin in input_char_pinyins:
            # 查找所有具有相同拼音的字符
            if input_pinyin in pinyin_to_chars:
                matching_chars = pinyin_to_chars[input_pinyin]
                
                # 在costume数据中查找包含这些字符的项目
                for item in d:
                    idx = 0
                    while idx < len(item['name']):
                        if item['name'][idx].isalpha():
                            item_char = item['name'][idx].lower()
                            if item_char in matching_chars:
                                # 避免重复添加同一个item
                                item_id = item.get('id', item['name'])  # 使用id或name作为唯一标识
                                if item_id not in matched_items:
                                    matched_items.add(item_id)
                                    # 添加标记，标识是否完全匹配输入字符
                                    item_copy = item.copy()
                                    item_copy['exact_match'] = (item_char == char)
                                    item_copy['matched_char'] = item_char
                                    item_copy['matched_pinyin'] = input_pinyin
                                    matching_costumes.append(item_copy)
                            break
                        idx += 1
        
        # 按匹配优先级排序：完全匹配的字符排在前面
        matching_costumes.sort(key=lambda x: (not x['exact_match'], x['name']))
        result.append(matching_costumes)
    
    return result


if __name__ == '__main__':
    result = get_matching_costumes('你')
    print(result)