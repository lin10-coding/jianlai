from flask import Flask, send_from_directory, jsonify, request
import os

app = Flask(__name__)

# 图片存放路径
SKILLS_DIR = os.path.join(os.getcwd(), 'static', 'skills')
POTIONS_DIR = os.path.join(os.getcwd(), 'static', 'potions')
EQUIPMENTS_DIR = os.path.join(os.getcwd(), 'static', 'equipment')

# 为了安全起见，允许从这些目录返回文件
ALLOWED_DIRECTORIES = {
    'skills': SKILLS_DIR,
    'potions': POTIONS_DIR,
    'equipment': EQUIPMENTS_DIR
}

# 请求功法图片
@app.route('/image/skill/<filename>')
def get_skill_image(filename):
    return send_image_from_directory('skills', filename)

# 请求丹药图片
@app.route('/image/potion/<filename>')
def get_potion_image(filename):
    return send_image_from_directory('potions', filename)

# 请求装备图片
@app.route('/image/equipment/<filename>')
def get_equipment_image(filename):
    return send_image_from_directory('equipment', filename)

# 图片请求处理
def send_image_from_directory(image_type, filename):
    # 确保请求的图片类型是合法的
    if image_type not in ALLOWED_DIRECTORIES:
        return jsonify({"error": "Invalid image type requested"}), 400

    directory = ALLOWED_DIRECTORIES[image_type]
    
    # 验证文件是否存在
    file_path = os.path.join(directory, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": f"{image_type} image not found"}), 404

    # 返回图片
    return send_from_directory(directory, filename)

// 请求功法图片
function getSkillImage(skillName) {
    fetch(`/image/skill/${skillName}.png`)
        .then(response => response.blob())
        .then(imageBlob => {
            const imageObjectURL = URL.createObjectURL(imageBlob);
            document.getElementById('skill-image').src = imageObjectURL;
        })
        .catch(error => console.error('Error fetching skill image:', error));
}

// 请求丹药图片
function getPotionImage(potionName) {
    fetch(`/image/potion/${potionName}.png`)
        .then(response => response.blob())
        .then(imageBlob => {
            const imageObjectURL = URL.createObjectURL(imageBlob);
            document.getElementById('potion-image').src = imageObjectURL;
        })
        .catch(error => console.error('Error fetching potion image:', error));
}

// 请求装备图片
function getEquipmentImage(equipmentName) {
    fetch(`/image/equipment/${equipmentName}.png`)
        .then(response => response.blob())
        .then(imageBlob => {
            const imageObjectURL = URL.createObjectURL(imageBlob);
            document.getElementById('equipment-image').src = imageObjectURL;
        })
        .catch(error => console.error('Error fetching equipment image:', error));
}



if __name__ == '__main__':
    app.run(debug=True)
