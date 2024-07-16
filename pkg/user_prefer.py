import json
import os

# 文件内容示例
# {
#   "123456": {
#     "switch": true,
#     "provider": "haitunAI",
#     "detail": {
#       "voice_id": "430",
#       "voice_name": "派蒙"
#     }
#   }
# }

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建绝对路径
file_path = os.path.join(current_dir, '..', 'data', 'preference.json')

# 如果目录和文件不存在则创建
if not os.path.exists(os.path.join(current_dir, '..')):
    os.mkdir(os.path.join(current_dir, '..'))
if not os.path.exists(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('{}')


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 查询用户偏好
def get_preference(user_id):
    # 检测内容，如果为空，则写入{}
    if os.path.getsize(file_path) == 0:
        write_json(file_path, {})
    # 如果user_id为数字，则转为字符串
    if isinstance(user_id, int):
        user_id = str(user_id)
    data = read_json(file_path)
    if user_id not in data:
        # print(f"用户 {user_id} 不存在。")
        return {}
    return data[user_id]


# 修改用户偏好,包括增改
def change_preference(user_id, content):
    # print(f"-------修改用户{user_id}的偏好为{content}")
    data = read_json(file_path)
    # content有三种形式，1是仅控制开关，2是只修改详细，3是控制开关和修改详细
    # 如果content中有switch和detail，则同时修改
    if "switch" in content and "detail" in content:
        data[user_id] = content
    # 如果content中只有switch，则直接修改开关
    if "switch" in content:
        data[user_id]["switch"] = content["switch"]
    # 如果content中只有detail，则直接修改详细
    if "detail" in content:
        data[user_id]["detail"] = content["detail"]

    write_json(file_path, data)
    return content
