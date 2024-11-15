import json
from flask import current_app
import requests
from flask import Blueprint
from flask_login import current_user

apprentice= Blueprint('apprenticeAI',__name__)

@apprentice.route('/apprenticeAI')
def apprenticeAI():
    player_id = current_user.get_id()
    connection = current_app.config['CONNECTION']
    with connection.cursor() as cursor:
        cursor.execute("SELECT year FROM player WHERE player_id = %s", (player_id,))
        result = cursor.fetchone()
        year = result['year']
    url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
    data = {"max_tokens": 4096, "top_k": 4, "temperature": 0.5, "messages": [
        {
            "role": "system",
            "content": "你是一个修仙世界的旁白,根据我发送第几年，给出剧情,一两句话就好"
        },
        {
            "role": "user",
            "content": '第'+str(year)+'年'
        }
    ], "model": "generalv3.5", "stream": True}
    header = {
        "Authorization": "Bearer VSjYPSByEwNEwDLkdJFS:WWkBQcXnjCoaNJYzgAXD"
    }
    response = requests.post(url, headers=header, json=data, stream=True)

    # 流式响应解析示例
    response.encoding = "utf-8"
    full_content = ""  # 初始化一个变量来存储完整的content
    for line in response.iter_lines(decode_unicode="utf-8"):
        if line and line.startswith("data: "):  # 确保line不为空并且以"data: "开头
            json_str = line[6:]  # 去掉"data: "前缀
            try:
                if (len(json_str)) > 8:
                    json_line = json.loads(json_str)
                    print(json_line)
                    choices = json_line.get("choices", [])
                    for choice in choices:
                        content = choice.get("delta", {}).get("content", "")
                        full_content += content  # 将新的content添加到full_content变量中
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")  # 打印错误信息并继续处理下一行
    with connection.cursor() as cursor:
        cursor.execute("update player set year = %s where player_id = %s", ((year+1),player_id))
        connection.commit()
    return full_content