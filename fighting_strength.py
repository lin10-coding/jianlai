from flask import current_app, Blueprint, jsonify
from flask_login import current_user

# 创建蓝图
calculate_fighting_strength = Blueprint('calculate_fighting_strength', __name__)

@calculate_fighting_strength.route('/calculate_fighting_strength')
def calculate_fighting_strengthFun():
    player_id = current_user.get_id()  # 获取当前用户 ID
    connection = current_app.config['CONNECTION']  # 从配置中获取数据库连接

    # 查询玩家属性和等级
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT root_bone, charm, family_back_ground, insight, fate, physique, level 
            FROM player WHERE player_id = %s
        """, (player_id,))
        result = cursor.fetchone()

        # 检查查询结果
        if not result:
            return jsonify({"error": "Player not found"}), 404

        # 获取属性值
        root_bone = result['root_bone']
        charm = result['charm']
        family_back_ground = result['family_back_ground']
        insight = result['insight']
        fate = result['fate']
        physique = result['physique']
        level = result['level']
        print('----------------------------------------------------------')
        print('----------------------------------------------------------')
        print('----------------------------------------------------------')
        print(root_bone)
        print(charm)
    # 根据六维属性和等级计算战力
    level_strength = level * 100  # 每个等级增加 100 战力
    attribute_bonus = (root_bone + insight + physique) / 100  # 六维属性加成
    fighting_strength = level_strength * (1+attribute_bonus)

    # 返回战力结果
    return jsonify({"fighting_strength": fighting_strength}), 200
