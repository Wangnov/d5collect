import json
from pypinyin import pinyin, Style

# 处理拼音
"""将所有汉字转换为拼音"""
with open('costumes_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
character_list = []
for i in d:
    idx = 0
    while idx < len(i['name']):
        if i['name'][idx].isalpha():
            character_list.append(i['name'][idx].lower())
            break
        idx += 1
pinyin_dict = {char: pinyin(char, style=Style.NORMAL)[0][0] for char in character_list}

def get_matching_costumes(input_str):
    """
    获取输入字符串中每个汉字对应的读音相同的costume内容列表
    :param input_str: 用户输入的汉字字符串
    :return: 按输入顺序排列的每个汉字对应的costume内容列表（嵌套列表形式）
    """
    input_str = input_str.lower()  # 转换为小写以支持大小写不敏感匹配
    result = []
    
    for char in input_str:
        if char in pinyin_dict:
            char_pinyin = pinyin_dict[char]
            matching_costumes = []
            for item in d:
                idx = 0
                while idx < len(item['name']):
                    if item['name'][idx].isalpha():
                        item_pinyin = pinyin(item['name'][idx].lower(), style=Style.NORMAL)[0][0]
                        if item_pinyin == char_pinyin:
                            # 添加标记，标识是否完全匹配输入字符
                            item_copy = item.copy()
                            item_copy['exact_match'] = (item['name'][idx].lower() == char)
                            matching_costumes.append(item_copy)
                        break
                    idx += 1
            result.append(matching_costumes)
        else:
            # 如果字符不在pinyin_dict中，尝试直接获取其拼音进行匹配
            try:
                char_pinyin = pinyin(char, style=Style.NORMAL)[0][0]
                matching_costumes = []
                for item in d:
                    idx = 0
                    while idx < len(item['name']):
                        if item['name'][idx].isalpha():
                            item_pinyin = pinyin(item['name'][idx].lower(), style=Style.NORMAL)[0][0]
                            if item_pinyin == char_pinyin:
                                # 添加标记，标识是否完全匹配输入字符
                                item_copy = item.copy()
                                item_copy['exact_match'] = (item['name'][idx].lower() == char)
                                matching_costumes.append(item_copy)
                            break
                        idx += 1
                result.append(matching_costumes)
            except Exception:
                result.append([])
    
    return result


if __name__ == '__main__':
    result = get_matching_costumes('你')
    print(result)