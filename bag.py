from flask import Blueprint, jsonify, request
from flask_login import current_user
import re
get_items_bp = Blueprint('get_items', __name__)
equip_items_bp = Blueprint('equip_item', __name__)
unequip_items_bp = Blueprint('unequip_item', __name__)
use_alchemy_bp = Blueprint('use_alchemy', __name__)
@get_items_bp.route('/get_items', methods=['GET'])
def get_items():
    from main import app  # 延迟导入以避免循环依赖

    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "用户未登录"}), 401

    player_id = current_user.get_id()
    if not player_id:
        return jsonify({"success": False, "message": "无效的用户 ID"}), 400

    app.logger.debug(f"当前用户 ID: {player_id}，类型: {type(player_id)}")

    try:
        with app.config['CONNECTION'].cursor() as cursor:
            query_items = "SELECT item_id FROM player_item WHERE player_id = %s"
            cursor.execute(query_items, (player_id,))
            items = [{"img": f"../static/zhuangbei_{row['item_id']}.png", "name": f"装备 {row['item_id']}"} for row in cursor.fetchall()]

            query_skills = "SELECT skill_id FROM player_skill WHERE player_id = %s"
            cursor.execute(query_skills, (player_id,))
            skills = [{"img": f"../static/skill_{row['skill_id']}.png", "name": f"功法 {row['skill_id']}"} for row in cursor.fetchall()]

            query_alchemy = "SELECT alchemy_id FROM player_alchemy WHERE player_id = %s"
            cursor.execute(query_alchemy, (player_id,))
            alchemy = [{"img": f"../static/alchemy_{row['alchemy_id']}.png", "name": f"丹药 {row['alchemy_id']}"} for row in cursor.fetchall()]

        return jsonify({
            "success": True,
            "equipment": items,
            "techniques": skills,
            "elixirs": alchemy
        })
    except Exception as e:
        app.logger.error(f"数据库查询错误: {e}")
        return jsonify({"success": False, "message": "服务器内部错误"}), 500

@get_items_bp.route('/equip_item', methods=['POST'])
def equip_item():
    from main import app
    data = request.get_json()
    player_id = current_user.get_id()
    item_id_str = data.get('item_id')  # 接收到的可能是 "装备 2"
    print(item_id_str)
    
    # 使用正则表达式提取数字部分
    match = re.search(r'\d+', item_id_str)
    if not match:
        return jsonify({"success": False, "message": "无效的装备 ID"}), 400

    item_id = int(match.group())  # 将提取的数字字符串转换为整数
    if not item_id:
        return jsonify({"success": False, "message": "缺少装备 ID"}), 400

    try:
        with app.config['CONNECTION'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM player_item WHERE player_id = %s AND equipped = 1", (player_id,))
            equipped_count = cursor.fetchone()['COUNT(*)']

            if equipped_count >= 4:
                return jsonify({"success": False, "message": "最多可以装备 4 个装备"}), 400
            print(item_id)
            cursor.execute("UPDATE player_item SET equipped = 1 WHERE player_id = %s AND item_id = %s", (player_id, item_id))
            
            app.config['CONNECTION'].commit()

        return jsonify({"success": True, "message": "装备成功"})
    except Exception as e:
        app.logger.error(f"装备操作失败: {e}")
        return jsonify({"success": False, "message": "服务器内部错误"}), 500

@get_items_bp.route('/unequip_item', methods=['POST'])
def unequip_item():
    from main import app
    data = request.get_json()
    player_id = current_user.get_id()
    item_id_str = data.get('item_id')  # 接收到的可能是 "装备 2"
    
    # 使用正则表达式提取数字部分
    match = re.search(r'\d+', item_id_str)
    if not match:
        return jsonify({"success": False, "message": "无效的装备 ID"}), 400

    item_id = int(match.group())  # 将提取的数字字符串转换为整数
    if not item_id:
        return jsonify({"success": False, "message": "缺少装备 ID"}), 400

    try:
        with app.config['CONNECTION'].cursor() as cursor:
            cursor.execute("UPDATE player_item SET equipped = 0 WHERE player_id = %s AND item_id = %s", (player_id, item_id))
            app.config['CONNECTION'].commit()

        return jsonify({"success": True, "message": "卸下装备成功"})
    except Exception as e:
        app.logger.error(f"卸下装备失败: {e}")
        return jsonify({"success": False, "message": "服务器内部错误"}), 500

@get_items_bp.route('/use_alchemy', methods=['POST'])
def use_alchemy():
    from main import app
    data = request.get_json()
    player_id = current_user.get_id()
    alchemy_id = data.get('alchemy_id')

    if not alchemy_id:
        return jsonify({"success": False, "message": "缺少丹药 ID"}), 400

    try:
        with app.config['CONNECTION'].cursor() as cursor:
            cursor.execute("DELETE FROM player_alchemy WHERE player_id = %s AND alchemy_id = %s", (player_id, alchemy_id))
            app.config['CONNECTION'].commit()

        return jsonify({"success": True, "message": "丹药使用成功"})
    except Exception as e:
        app.logger.error(f"丹药使用失败: {e}")
        return jsonify({"success": False, "message": "服务器内部错误"}), 500
