from flask import Blueprint, request, jsonify
from flask_login import current_user
from config import CONNECTION  # 注意这里是大写的 CONNECTION

level_up_bp = Blueprint('level_up_bp', __name__, url_prefix='/level_up')

@level_up_bp.route('/upgrade', methods=['POST'])
def level_up():
    # 检查用户是否已登录
    if not current_user.is_authenticated:
        return jsonify({"error": "用户未登录"}), 401

    # 获取当前用户的 player_id
    player_id = current_user.get_id()
    if not player_id:
        return jsonify({"error": "无效的用户 ID"}), 400

    # 获取请求中的升级等级数量
    data = request.get_json()
    level_increment = data.get('level_increment', 0)
    try:
        level_increment = int(level_increment)
        if level_increment <= 0:
            return jsonify({"error": "升级等级必须为正整数"}), 400
    except ValueError:
        return jsonify({"error": "升级等级必须为整数"}), 400

    try:
        with CONNECTION.cursor() as cursor:
            # 获取玩家当前等级和经验值
            cursor.execute("SELECT level, current_exp FROM player WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()

            if not player:
                return jsonify({"error": "玩家未找到"}), 404

            current_level = player['level']
            current_exp = player['current_exp']

            # 获取目标等级
            target_level = current_level + level_increment

            # 获取从当前等级到目标等级所需的总经验值
            cursor.execute("""
                SELECT SUM(need_exp) AS total_exp_needed
                FROM level
                WHERE level > %s AND level <= %s
            """, (current_level, target_level))

            exp_needed_result = cursor.fetchone()
            exp_needed = exp_needed_result['total_exp_needed']

            if exp_needed is None:
                return jsonify({"error": "目标等级超出范围"}), 400

            # 判断经验值是否足够
            if current_exp >= exp_needed:
                # 扣除经验值，更新等级
                new_exp = current_exp - exp_needed
                new_level = target_level

                cursor.execute("""
                    UPDATE player
                    SET level = %s, current_exp = %s
                    WHERE player_id = %s
                """, (new_level, new_exp, player_id))
                CONNECTION.commit()

                # 获取新的等级名称
                cursor.execute("SELECT name FROM level WHERE level = %s", (new_level,))
                level_info = cursor.fetchone()
                level_name = level_info['name'] if level_info else "未知等级"

                return jsonify({
                    "message": "升级成功",
                    "new_level": new_level,
                    "remaining_exp": new_exp,
                    "level_name": level_name
                }), 200
            else:
                return jsonify({"error": "经验值不够"}), 400

    except Exception as e:
        CONNECTION.rollback()
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500

@level_up_bp.route('/get_player_info', methods=['GET'])
def get_player_info():
    # 检查用户是否已登录
    if not current_user.is_authenticated:
        return jsonify({"error": "用户未登录"}), 401

    # 获取当前用户的 player_id
    player_id = current_user.get_id()
    if not player_id:
        return jsonify({"error": "无效的用户 ID"}), 400

    try:
        with CONNECTION.cursor() as cursor:
            # 获取玩家的等级和当前经验值
            cursor.execute("SELECT level, current_exp FROM player WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()

            if not player:
                return jsonify({"error": "玩家未找到"}), 404

            # 获取等级名称
            cursor.execute("SELECT name FROM level WHERE level = %s", (player['level'],))
            level_info = cursor.fetchone()
            level_name = level_info['name'] if level_info else "未知等级"

            return jsonify({
                "success": True,
                "level": player['level'],
                "current_exp": player['current_exp'],
                "level_name": level_name
            }), 200

    except Exception as e:
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500

@level_up_bp.route('/get_level_name', methods=['GET'])
def get_level_name():
    level = request.args.get('level', type=int)
    if not level:
        return jsonify({"error": "未提供等级参数"}), 400

    try:
        with CONNECTION.cursor() as cursor:
            cursor.execute("SELECT name FROM level WHERE level = %s", (level,))
            level_info = cursor.fetchone()
            if not level_info:
                return jsonify({"error": "等级未找到"}), 404
            return jsonify({
                "success": True,
                "level_name": level_info['name']
            }), 200
    except Exception as e:
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500
