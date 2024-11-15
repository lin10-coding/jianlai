from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# 定义每种丹药的材料需求
alchemy_recipes = {
    "elixir1.png": ["material1", "material2"],
    "elixir2.png": ["material3", "material4"],
    "elixir3.png": ["material1", "material3"],
    "elixir4.png": ["material2", "material4"],
}

# 模拟炼丹的过程
def perform_alchemy(materials):
    # 模拟炼丹过程，耗时5秒
    time.sleep(5)
    
    # 检查传入的材料是否符合任何一个丹药的炼制配方
    for result_image, required_materials in alchemy_recipes.items():
        if sorted(materials) == sorted(required_materials):  # 材料配方匹配
            return result_image
    
    # 如果没有符合的配方
    return None

@app.route('/start_alchemy', methods=['POST'])
def start_alchemy():
    # 获取前端传来的材料列表
    materials = request.json.get('materials', [])
    
    # 如果没有材料，返回错误信息
    if not materials:
        return jsonify({"error": "请添加材料"}), 400
    
    # 调用炼丹函数并获取结果
    result_image = perform_alchemy(materials)
    
    # 如果没有炼成丹药，返回错误信息
    if result_image is None:
        return jsonify({"error": "材料不符合炼丹要求"}), 400
    
    # 返回炼丹结果的图片路径
    return jsonify({"result_image": result_image})

if __name__ == '__main__':
    app.run(debug=True)
