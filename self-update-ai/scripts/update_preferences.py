#!/usr/bin/env python3
"""
自更新 AI 偏好管理工具
用于读取和更新用户偏好配置文件
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def get_preferences_path():
    """获取偏好配置文件路径"""
    # 默认路径：用户主目录/.claude/self-update-ai/preferences.json
    home = Path.home()
    return home / ".claude" / "self-update-ai" / "preferences.json"


def load_preferences():
    """加载偏好配置"""
    path = get_preferences_path()
    if not path.exists():
        return create_default_preferences()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误：无法加载偏好配置 - {e}", file=sys.stderr)
        return create_default_preferences()


def create_default_preferences():
    """创建默认偏好配置"""
    default = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "writing_style": {
            "sentence_length": "medium",
            "max_sentences_per_paragraph": 5,
            "prefer_short_sentences": False,
            "forbidden_words": [],
            "preferred_words": []
        },
        "content_structure": {
            "intro_max_sentences": 3,
            "use_transitions": True,
            "bullet_points preferred": False
        },
        "tone": {
            "formality": "neutral",
            "verbosity": "medium"
        },
        "custom_rules": [],
        "feedback_history": []
    }

    # 保存默认配置
    save_preferences(default)
    return default


def save_preferences(preferences):
    """保存偏好配置"""
    path = get_preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    preferences['updated_at'] = datetime.now().isoformat()

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"错误：无法保存偏好配置 - {e}", file=sys.stderr)
        return False


def add_feedback(category, key, value, reason=""):
    """添加反馈到偏好配置"""
    preferences = load_preferences()

    # 更新配置
    if category not in preferences:
        preferences[category] = {}

    preferences[category][key] = value

    # 记录反馈历史
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "key": key,
        "value": value,
        "reason": reason
    }

    if "feedback_history" not in preferences:
        preferences["feedback_history"] = []

    preferences["feedback_history"].append(feedback_entry)

    # 只保留最近 50 条反馈历史
    if len(preferences["feedback_history"]) > 50:
        preferences["feedback_history"] = preferences["feedback_history"][-50:]

    return save_preferences(preferences)


def add_forbidden_word(word, reason=""):
    """添加禁用词汇"""
    preferences = load_preferences()
    word = word.strip()

    if "writing_style" not in preferences:
        preferences["writing_style"] = {}

    if "forbidden_words" not in preferences["writing_style"]:
        preferences["writing_style"]["forbidden_words"] = []

    if word not in preferences["writing_style"]["forbidden_words"]:
        preferences["writing_style"]["forbidden_words"].append(word)

        # 记录反馈历史
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": "writing_style",
            "key": "forbidden_words",
            "value": word,
            "reason": reason or f"用户禁用词汇: {word}"
        }

        if "feedback_history" not in preferences:
            preferences["feedback_history"] = []

        preferences["feedback_history"].append(feedback_entry)

    return save_preferences(preferences)


def add_custom_rule(rule_description, pattern=""):
    """添加自定义规则"""
    preferences = load_preferences()

    if "custom_rules" not in preferences:
        preferences["custom_rules"] = []

    rule_entry = {
        "id": f"rule_{len(preferences['custom_rules']) + 1}",
        "description": rule_description,
        "pattern": pattern,
        "created_at": datetime.now().isoformat()
    }

    preferences["custom_rules"].append(rule_entry)

    return save_preferences(preferences)


def print_preferences():
    """打印当前偏好配置"""
    preferences = load_preferences()
    print(json.dumps(preferences, ensure_ascii=False, indent=2))


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python update_preferences.py show                    # 显示当前配置")
        print("  python update_preferences.py add <category> <key> <value> [reason]")
        print("  python update_preferences.py forbid <word> [reason]  # 添加禁用词")
        print("  python update_preferences.py rule <description> [pattern]  # 添加规则")
        sys.exit(1)

    command = sys.argv[1]

    if command == "show":
        print_preferences()

    elif command == "add":
        if len(sys.argv) < 5:
            print("错误：缺少参数", file=sys.stderr)
            print("用法: python update_preferences.py add <category> <key> <value> [reason]")
            sys.exit(1)

        category = sys.argv[2]
        key = sys.argv[3]
        value = sys.argv[4]
        reason = sys.argv[5] if len(sys.argv) > 5 else ""

        # 尝试将 value 转换为合适的类型
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)

        if add_feedback(category, key, value, reason):
            print(f"[OK] 已更新配置: {category}.{key} = {value}")
        else:
            print("[ERROR] 更新失败", file=sys.stderr)
            sys.exit(1)

    elif command == "forbid":
        if len(sys.argv) < 3:
            print("错误：缺少参数", file=sys.stderr)
            print("用法: python update_preferences.py forbid <word> [reason]")
            sys.exit(1)

        word = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else ""

        if add_forbidden_word(word, reason):
            print(f"[OK] 已添加禁用词: {word}")
        else:
            print("[ERROR] 添加失败", file=sys.stderr)
            sys.exit(1)

    elif command == "rule":
        if len(sys.argv) < 3:
            print("错误：缺少参数", file=sys.stderr)
            print("用法: python update_preferences.py rule <description> [pattern]")
            sys.exit(1)

        description = sys.argv[2]
        pattern = sys.argv[3] if len(sys.argv) > 3 else ""

        if add_custom_rule(description, pattern):
            print(f"[OK] 已添加规则: {description}")
        else:
            print("[ERROR] 添加失败", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"错误：未知命令 '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
