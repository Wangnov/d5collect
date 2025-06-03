import json
import requests
import re
import time
from bs4 import BeautifulSoup

def get_latest_costume_count():
    """
    获取最新的时装总数
    """
    count_url = 'https://wiki.biligame.com/dwrg/api.php?format=json&action=parse&text=%7B%7B%23ask%3A%5B%5B%E5%88%86%E7%B1%BB%3A%E6%97%B6%E8%A3%85%5D%5D%7Cformat%3Dcount%7D%7D&contentmodel=wikitext'

    try:
        response = requests.get(count_url)
        response.raise_for_status()

        response_data = response.json()

        # 从HTML内容中提取数字
        html_content = response_data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')

        # 查找包含数字的p标签
        p_tag = soup.find('p')
        if p_tag:
            count_text = p_tag.get_text().strip()
            # 提取数字
            count = int(count_text)
            return count
        else:
            print("未找到时装总数信息")
            return None

    except requests.RequestException as e:
        print(f"获取时装总数失败: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        print(f"解析时装总数失败: {e}")
        return None

def extract_costume_data_from_response(response_data):
    """
    从API响应中提取符合costumes_data.json格式的数据
    """
    results = []

    # 获取HTML内容
    html_content = response_data['parse']['text']['*']

    # 获取图片文件名列表
    images = response_data['parse']['images']

    # 解析HTML以提取image_url和wiki_url
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有的时装卡片
    clothes_boxes = soup.find_all('div', class_='clothes-box')

    for i, box in enumerate(clothes_boxes):
        if i >= len(images):
            break

        # 提取wiki_url
        link_element = box.find('a')
        if link_element and 'href' in link_element.attrs:
            wiki_url = 'https://wiki.biligame.com' + link_element['href']
        else:
            wiki_url = ""

        # 提取image_url (使用120px版本)
        img_element = box.find('img')
        if img_element and 'srcset' in img_element.attrs:
            # 从srcset中提取120px版本的URL
            srcset = img_element['srcset']
            # 查找120px版本
            match = re.search(r'(https://[^\s]+120px-[^\s]+)\s+2x', srcset)
            if match:
                image_url = match.group(1)
            else:
                image_url = img_element.get('src', '')
        else:
            image_url = ""

        # 从图片文件名中提取信息
        image_filename = images[i]

        # 正则提取角色、品质和名称
        # 格式通常是：角色+品质+时装_名称.png
        pattern = r'^(.+?)(罕见品质|独特品质|奇珍品质|稀世品质|虚妄杰作品质)时装_(.+)\.png$'
        match = re.match(pattern, image_filename)

        if match:
            character = match.group(1)
            quality_name = match.group(2)
            name = match.group(3)

            # 映射品质名称到数字
            quality_map = {
                '罕见品质': 0,
                '独特品质': 1,
                '奇珍品质': 2,
                '稀世品质': 3,
                '虚妄杰作品质': 4
            }
            quality = quality_map.get(quality_name, 0)

            costume_data = {
                "character": character,
                "quality": quality,
                "quality_name": quality_name,
                "name": name,
                "image_url": image_url,
                "wiki_url": wiki_url
            }

            results.append(costume_data)

    return results


def use_api_request():
    """
    使用URL请求获取数据
    """
    print("\n=== 使用API请求 ===")

    url = 'https://wiki.biligame.com/dwrg/api.php?format=json&action=parse&text=%7B%7B%23ask%3A%5B%5B%E5%88%86%E7%B1%BB%3A%E6%97%B6%E8%A3%85%5D%5D%7C%3F%E5%90%8D%E7%A7%B0%7C%3F%E8%A7%92%E8%89%B2%7C%3F%E5%93%81%E8%B4%A8%7C%3F%E4%BB%B7%E6%A0%BC%7C%3F%E5%85%B7%E4%BD%93%E6%8F%8F%E8%BF%B0%7C%3F%E5%9B%BE%E9%89%B4%E5%B1%9E%E6%80%A7%7C%3F%E7%BC%96%E5%8F%B7%7Csort%3D%E5%90%8D%E7%A7%B0%7Ctemplate%3D%E9%80%9A%E7%94%A8%E5%88%97%E8%A1%A8%7Cheaders%3Dhide%7Cformat%3Dtemplate%7Clink%3Dnone%7Climit%3D10%7Coffset%3D0%7D%7D%0A&contentmodel=wikitext'

    try:
        response = requests.get(url)
        response.raise_for_status()

        response_data = response.json()

        # 提取数据
        extracted_data = extract_costume_data_from_response(response_data)

        # 打印结果
        for item in extracted_data:
            print(json.dumps(item, ensure_ascii=False, indent=2))

        return extracted_data

    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return []

def build_api_url(limit=100, offset=0):
    """
    构建API请求URL，支持分页参数
    参考正确的API结构
    """
    # 直接使用正确的URL模板，只替换limit和offset参数
    # 这是从你提供的正确API结构中提取的模板
    url = f"https://wiki.biligame.com/dwrg/api.php?format=json&action=parse&text=%7B%7B%23ask%3A%5B%5B%E5%88%86%E7%B1%BB%3A%E6%97%B6%E8%A3%85%5D%5D%7C%3F%E5%90%8D%E7%A7%B0%7C%3F%E8%A7%92%E8%89%B2%7C%3F%E5%93%81%E8%B4%A8%7C%3F%E4%BB%B7%E6%A0%BC%7C%3F%E5%85%B7%E4%BD%93%E6%8F%8F%E8%BF%B0%7C%3F%E5%9B%BE%E9%89%B4%E5%B1%9E%E6%80%A7%7C%3F%E7%BC%96%E5%8F%B7%7Csort%3D%E5%90%8D%E7%A7%B0%7Ctemplate%3D%E9%80%9A%E7%94%A8%E5%88%97%E8%A1%A8%7Cheaders%3Dhide%7Cformat%3Dtemplate%7Clink%3Dnone%7Climit%3D{limit}%7Coffset%3D{offset}%7D%7D%0A&contentmodel=wikitext"

    return url

def collect_all_costume_data(total_count):
    """
    采集全部时装数据
    """
    print(f"\n=== 开始全量数据采集 ===")
    print(f"目标数据量: {total_count}")

    # 计算预估时间
    limit = 100
    total_pages = (total_count + limit - 1) // limit  # 向上取整
    estimated_minutes = total_pages  # 每页1分钟间隔
    print(f"预计需要 {total_pages} 页，约 {estimated_minutes} 分钟")

    all_data = []
    offset = 0
    page = 1
    start_time = time.time()

    while offset < total_count:
        print(f"\n--- 第 {page} 页 (offset: {offset}, limit: {limit}) ---")

        # 构建API URL
        url = build_api_url(limit=limit, offset=offset)

        try:
            # 发送请求
            response = requests.get(url)
            response.raise_for_status()

            response_data = response.json()

            # 提取数据
            page_data = extract_costume_data_from_response(response_data)

            if not page_data:
                print("本页无数据，停止采集")
                break

            all_data.extend(page_data)

            # 计算进度
            progress = min(len(all_data) / total_count * 100, 100)
            elapsed_time = time.time() - start_time

            print(f"本页获取 {len(page_data)} 条数据，累计 {len(all_data)} 条")
            print(f"进度: {progress:.1f}% ({len(all_data)}/{total_count})")
            print(f"已用时: {elapsed_time/2:.1f} 分钟")

            # 更新分页参数
            offset += limit
            page += 1

            # 如果不是最后一页，等待1分钟
            if offset < total_count:
                print("等待 2 秒后继续...")
                time.sleep(2)

        except requests.RequestException as e:
            print(f"第 {page} 页请求失败: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"第 {page} 页JSON解析失败: {e}")
            break
        except Exception as e:
            print(f"第 {page} 页处理失败: {e}")
            break

    # 计算总用时
    total_time = time.time() - start_time

    print(f"\n=== 数据采集完成 ===")
    print(f"总共采集到 {len(all_data)} 条数据")
    print(f"总用时: {total_time/2:.1f} 分钟")
    print(f"采集效率: {len(all_data)/(total_time/2):.1f} 条/分钟")

    return all_data

def save_updated_data(data, filename="costumes_data_updated.json"):
    """
    保存更新后的数据到新文件
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def test_api_url():
    """
    测试API URL是否正确工作
    """
    print("=== 测试API URL ===")
    test_url = build_api_url(limit=10, offset=0)
    print(f"测试URL: {test_url}")

    try:
        response = requests.get(test_url)
        response.raise_for_status()
        response_data = response.json()

        # 检查响应结构
        if 'parse' in response_data and 'text' in response_data['parse']:
            print("✅ API响应结构正确")

            # 尝试提取数据
            test_data = extract_costume_data_from_response(response_data)
            print(f"✅ 成功提取到 {len(test_data)} 条测试数据")

            if test_data:
                print("测试数据示例:")
                print(json.dumps(test_data[0], ensure_ascii=False, indent=2))

            return True
        else:
            print("❌ API响应结构异常")
            return False

    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    # 首先测试API URL是否正确
    if not test_api_url():
        print("API测试失败，请检查URL结构")
        return

    # 检测最新的时装总数
    print("\n=== 检测最新时装总数 ===")
    latest_count = get_latest_costume_count()
    if latest_count:
        print(f"最新时装总数: {latest_count}")
    else:
        print("无法获取最新时装总数")
        return

    # 读取现有的costumes_data.json以了解数据结构
    try:
        with open('costumes_data.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        print(f"\n现有数据条数: {len(existing_data)}")
        print("现有数据示例:")
        print(json.dumps(existing_data[0], ensure_ascii=False, indent=2))

        # 比较数量差异
        need_update = False
        if latest_count > len(existing_data):
            print(f"\n发现新增时装: {latest_count - len(existing_data)} 件")
            print("需要更新数据...")
            need_update = True
        elif latest_count == len(existing_data):
            print("\n数据已是最新，无需更新")
        else:
            print(f"\n警告: 本地数据({len(existing_data)})多于远程数据({latest_count})")
            print("建议重新采集数据...")
            need_update = True

    except FileNotFoundError:
        print("\n未找到 costumes_data.json 文件")
        print("将创建新的数据文件...")
        existing_data = []
        need_update = True

    # 如果需要更新，执行全量数据采集
    if need_update:
        print(f"\n开始执行数据更新...")

        # 询问用户是否确认更新
        user_input = input(f"确认要采集全部 {latest_count} 条数据吗？这可能需要较长时间 (y/n): ")
        if user_input.lower() in ['y', 'yes', '是', '确认']:
            # 执行全量数据采集
            updated_data = collect_all_costume_data(latest_count)

            if updated_data:
                # 保存到新文件
                if save_updated_data(updated_data):
                    print(f"\n=== 更新完成 ===")
                    print(f"新数据已保存到 costumes_data_updated.json")
                    print(f"采集到 {len(updated_data)} 条数据")

                    # 数据质量检查
                    if len(updated_data) >= latest_count * 0.9:  # 允许10%的误差
                        print("✅ 数据采集质量良好")
                    else:
                        print(f"⚠️  数据采集可能不完整，预期 {latest_count} 条，实际 {len(updated_data)} 条")
                else:
                    print("❌ 数据保存失败")
            else:
                print("❌ 数据采集失败")
        else:
            print("用户取消更新")
    else:
        # 如果不需要更新，执行原有的小量测试
        print("\n执行小量数据测试...")
        api_results = use_api_request()

        print(f"\n=== 测试结果 ===")
        print(f"最新时装总数: {latest_count}")
        print(f"测试提取到 {len(api_results)} 条数据")

if __name__ == "__main__":
    main()