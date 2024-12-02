from flask import Flask, jsonify, request, abort, url_for, current_app
import time
from flask_login import current_user
from flask import Blueprint
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)

alchemy = Blueprint('start_alchemy', __name__)

# 定义每种丹药的材料需求和对应的alchemy_id
alchemy_recipes = {
    "alchemy_1.png": [["1", "1"], 1],
    "alchemy_2.png": [["1", "2"], 2],
    "alchemy_3.png": [["1", "3"], 3],            
    "alchemy_4.png": [["2", "2"], 4],  
    "alchemy_5.png": [["2", "3"], 5],  
    "alchemy_6.png": [["3", "3"], 6],  
}

# 模拟炼丹过程并插入数据库
def perform_alchemy(materials):
    # 模拟炼丹过程（延时0.1秒）
    time.sleep(0.1)

    # 检查传入的材料是否符合任何一个配方
    for result_image, (required_materials, alchemy_id) in alchemy_recipes.items():
        if sorted(materials) == sorted(required_materials):  # 匹配成功
            return result_image, alchemy_id
    return None, None  # 没有匹配的配方

@alchemy.route('/start_alchemy', methods=['POST'])
def start_alchemy():
    connection = current_app.config['CONNECTION']

    # 确保请求中包含JSON数据
    if not request.is_json:
        abort(400, description="请求必须包含JSON数据")

    # 获取前端传来的材料列表
    materials = request.json.get('materials', [])
    logging.debug(f"接收到的材料: {materials}")

    # 如果没有材料，返回错误
    if not materials:
        abort(400, description="请提供材料")

    # 获取当前用户的ID
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    player_id = current_user.get_id()
    if not player_id:
        return jsonify({"success": False, "message": "无效的用户 ID"}), 400

    # 调用炼丹函数并获取结果
    result_image, alchemy_id = perform_alchemy(materials)

    # 如果没有符合的配方，返回错误
    if result_image is None:
        abort(400, description="材料不符合炼丹要求")  

    # 插入数据到数据库
    try:
        with connection.cursor() as cursor:
            # 插入player_alchemy表，记录当前玩家的alchemy_id
            insert_query = "INSERT INTO player_alchemy (player_id, alchemy_id) VALUES (%s, %s)"
            cursor.execute(insert_query, (player_id, alchemy_id))
            connection.commit()  # 提交事务

            logging.debug(f"成功插入 player_id={player_id}, alchemy_id={alchemy_id}")

    except Exception as e:
        logging.error(f"数据库插入错误: {e}")
        return jsonify({"success": False, "message": "数据库插入错误"}), 500

    # 返回炼丹结果的图片路径
    result_image_url = url_for('static', filename=result_image)
    return jsonify({"result_image": result_image_url})
