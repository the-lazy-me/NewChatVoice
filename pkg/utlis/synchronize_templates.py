import os
import shutil
import json


def read_json_config(file_path):
    """
    读取 JSON 配置文件并返回字典。

    :param file_path: 配置文件路径
    :return: 配置字典
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_json_config(file_path, config):
    """
    将字典写入 JSON 配置文件。

    :param file_path: 配置文件路径
    :param config: 配置字典
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


def update_config_with_missing_keys(template_config, target_config):
    """
    更新目标配置字典，添加缺失的键。

    :param template_config: 模板配置字典
    :param target_config: 目标配置字典
    :return: 是否有更新
    """
    updated = False
    for key, value in template_config.items():
        if key not in target_config:
            target_config[key] = value
            updated = True
        elif isinstance(value, dict) and isinstance(target_config.get(key), dict):
            if update_config_with_missing_keys(value, target_config[key]):
                updated = True
    return updated


def synchronize_templates(template_folder, target_folder):
    """
    从模板文件夹中复制所有文件和文件夹到目标文件夹，并检查和更新 JSON 配置文件中的缺失键。

    :param template_folder: 模板文件夹路径
    :param target_folder: 目标文件夹路径
    """
    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 遍历模板文件夹中的所有项目
    for item in os.listdir(template_folder):
        source_path = os.path.join(template_folder, item)
        target_path = os.path.join(target_folder, item)

        if os.path.isfile(source_path):
            if os.path.exists(target_path):
                # 如果目标文件已存在，进行配置项检查和更新
                template_config = read_json_config(source_path)
                target_config = read_json_config(target_path)
                if update_config_with_missing_keys(template_config, target_config):
                    print(f"文件 {target_path} 缺失的配置项已更新")
                    write_json_config(target_path, target_config)
            else:
                # 如果目标文件不存在，直接复制
                shutil.copy2(source_path, target_path)

        elif os.path.isdir(source_path):
            # 递归处理文件夹
            synchronize_templates(source_path, target_path)
