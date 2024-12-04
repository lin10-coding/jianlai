from flask import Blueprint, request, jsonify
from flask_login import current_user
from config import CONNECTION  # 确保与您的项目配置一致
import re

# 创建蓝图
cultivation_bp = Blueprint('cultivation_bp', __name__, url_prefix='/cultivation')

# 开始闭关修炼的路由
@cultivation_bp.route('/start', methods=['POST'])
def start_cultivation():
    # 检查用户是否已登录
    if not current_user.is_authenticated:
        return jsonify({"error": "用户未登录"}), 401

    # 获取当前用户的 player_id
    player_id = current_user.get_id()
    if not player_id:
        return jsonify({"error": "无效的用户 ID"}), 400

    # 获取请求中的闭关天数
    data = request.get_json()
    duration_days = data.get('duration_days', 0)
    try:
        duration_days = float(duration_days)
    except ValueError:
        return jsonify({"error": "闭关时间必须为数字"}), 400

    if duration_days <= 0:
        return jsonify({"error": "闭关时间必须大于0"}), 400

    # 将天数转换为小时数
    duration_hours = duration_days * 24

    try:
        with CONNECTION.cursor() as cursor:
            # 获取玩家当前经验值
            cursor.execute("SELECT current_exp FROM player WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()

            if not player:
                return jsonify({"error": "玩家未找到"}), 404

            current_exp = player['current_exp']

            # 获取玩家的功法加成
            cursor.execute("""
                SELECT s.effect
                FROM player_skill ps
                JOIN skill s ON ps.skill_id = s.skill_id
                WHERE ps.player_id = %s
            """, (player_id,))
            skills = cursor.fetchall()

            total_cultivation_effect = 0
            for skill in skills:
                effect = skill.get('effect', '')
                match = re.search(r'加速修炼(\d+)%', effect)
                if match:
                    bonus_percentage = int(match.group(1))
                    total_cultivation_effect += bonus_percentage

            # 计算实际获得的经验值
            base_exp_per_hour = 10  # 基础每小时经验值，可根据需要调整
            total_exp_per_hour = base_exp_per_hour * (1 + total_cultivation_effect / 100)
            gained_exp = duration_hours * total_exp_per_hour
            new_exp = current_exp + gained_exp

            # 更新玩家经验值
            cursor.execute("""
                UPDATE player
                SET current_exp = %s
                WHERE player_id = %s
            """, (new_exp, player_id))
            CONNECTION.commit()

        return jsonify({
            "message": "修炼成功",
            "new_exp": new_exp
        }), 200

    except Exception as e:
        CONNECTION.rollback()
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500

# 获取玩家信息的路由
@cultivation_bp.route('/get_player_info', methods=['GET'])
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

            current_level = player['level']
            current_exp = player['current_exp']

            # 获取等级名称
            cursor.execute("SELECT name FROM level WHERE level = %s", (current_level,))
            level_info = cursor.fetchone()
            level_name = level_info['name'] if level_info else "未知等级"

            return jsonify({
                "success": True,
                "level": current_level,
                "current_exp": current_exp,
                "level_name": level_name
            }), 200

    except Exception as e:
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500

# 获取等级名称的路由
@cultivation_bp.route('/get_level_name', methods=['GET'])
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
