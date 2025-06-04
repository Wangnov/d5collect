import logging
from flask import Flask, render_template, request
from pinyin import get_matching_costumes
import json
from .tasks import update_costumes_task

# 配置日志
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# 加载皮肤数据
with open('costumes_data.json', 'r', encoding='utf-8') as f:
    costumes_data = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    input_text = None
    result = []
    user_ip = request.remote_addr

    if request.method == 'POST':
        input_text = request.form.get('input_text')
        if input_text:
            costumes = get_matching_costumes(input_text)
            result = list(zip(input_text, costumes))
            # 使用logger记录日志
            logging.info(f"用户IP: {user_ip} | 输入内容: {input_text} | 匹配结果: {len(result)}个匹配")
    return render_template('index.html', 
                          input_text=input_text,
                          result=result)

@app.route('/update_data_async', methods=['POST'])
def update_data_async():
    update_costumes_task.delay()
    return "Data update initiated in background!", 202

if __name__ == '__main__':
    app.run(debug=True, port=9877)