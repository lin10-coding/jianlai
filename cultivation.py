import pymysql
import re

# 数据库连接参数
host = '81.70.22.101'  # 数据库服务器地址
user = 'root'  # 数据库用户名
password = 'yabdylm'  # 数据库密码
database = 'swordCome'  # 数据库名

# 建立连接
connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             database=database,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# 根据功法的效果进行修炼加成
def calculate_cultivation_effect(player_id, duration_days):
    # 获取玩家的修炼功法
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.effect
            FROM player_skill ps
            JOIN skill s ON ps.skill_id = s.skill_id
            WHERE ps.player_id = %s
        """, (player_id,))
        skills = cursor.fetchall()

    # 计算修炼的效果（只考虑加速修炼）
    total_cultivation_effect = 0
    for skill in skills:
        effect = skill.get('effect', '')
        # 查找类似 "加速修炼X%" 的文本
        match = re.search(r'加速修炼(\d+)%', effect)
        if match:
            bonus_percentage = int(match.group(1))  # 获取加速百分比
            total_cultivation_effect += bonus_percentage  # 累加加速百分比
    
    # 根据修炼效果计算实际修炼时间
    actual_cultivation_time = duration_days * (1 - total_cultivation_effect / 100)

    return actual_cultivation_time

# 进行闭关修炼并保存经验
def start_cultivation(player_id, duration_days):
    # 计算修炼加成
    actual_cultivation_time = calculate_cultivation_effect(player_id, duration_days)

    # 获取玩家当前的修炼经验
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_exp FROM player WHERE player_id = %s", (player_id,))
        player = cursor.fetchone()

    if not player:
        return {"error": "Player not found"}, 404

    current_exp = player['current_exp']

    # 更新玩家的修炼经验
    new_exp = current_exp + actual_cultivation_time * 10  # 假设每单位时间增加10经验值

    # 更新玩家经验
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE player
            SET current_exp = %s
            WHERE player_id = %s
        """, (new_exp, player_id))
        connection.commit()

    return {"message": "Cultivation started successfully", "new_exp": new_exp}, 200

# 修炼升级
def level_up(player_id, used_exp):
    # 获取玩家当前经验和等级
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_exp, level FROM player WHERE player_id = %s", (player_id,))
        player = cursor.fetchone()

    if not player:
        return {"error": "Player not found"}, 404

    current_exp = player['current_exp']
    current_level = player['level']

    # 检查经验是否足够
    if used_exp > current_exp:
        return {"error": "Not enough experience for level up"}, 400

    # 减去用于升级的经验
    new_exp = current_exp - used_exp

    # 获取下一个等级所需经验
    with connection.cursor() as cursor:
        cursor.execute("SELECT need_exp FROM level WHERE level = %s", (current_level + 1,))
        next_level = cursor.fetchone()

    if not next_level:
        return {"error": "Next level not found"}, 404

    # 检查是否可以升级
    if used_exp >= next_level['need_exp']:
        new_level = current_level + 1
        # 更新玩家经验和等级
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE player
                SET current_exp = %s, level = %s
                WHERE player_id = %s
            """, (new_exp, new_level, player_id))
            connection.commit()
        return {"message": "Level up successful", "new_level": new_level, "new_exp": new_exp}, 200
    else:
        return {"error": "Not enough experience for level up"}, 400
