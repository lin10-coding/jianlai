import pymysql
import re

# 数据库连接参数
host = '81.70.22.101'  # 数据库服务器地址
user = 'root'  # 数据库用户名
password = 'yabdylm'  # 数据库密码
database = 'swordCome'  # 数据库名

# 建立连接
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 计算玩家的战力
def calculate_fighting_strength(player):
    # 获取玩家的六维属性
    root_bone = player['root_bone']
    insight = player['insight']
    physique = player['physique']
    level = player['level']
    
    # 根据六维属性和等级来计算基础战力
    level_strength = level * 100  # 每个等级增加 100 战力
    attribute_bonus = (root_bone + insight + physique) / 100  # 六维属性加成

    # 初始战力计算
    fighting_strength = level_strength * (1 + attribute_bonus)

    # 获取玩家的功法效果，查找是否有增加战力的效果
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.effect
            FROM player_skill_method ps
            JOIN skill_method s ON ps.skill_id = s.skill_id
            WHERE ps.player_id = %s
        """, (player['player_id'],))
        skills = cursor.fetchall()

    # 计算战力的增幅
    total_strength_bonus = 0
    for skill in skills:
        effect = skill.get('effect', '')
        # 查找类似 "增加战力X%" 的效果
        match = re.search(r'增加战力(\d+)%', effect)
        if match:
            bonus_percentage = int(match.group(1))  # 获取增加的战力百分比
            total_strength_bonus += bonus_percentage  # 累加所有功法的战力加成
    
    # 将战力加成应用到战力计算中
    fighting_strength *= (1 + total_strength_bonus / 100)

    return {"fighting_strength": fighting_strength}, 200
