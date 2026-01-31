#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def clean_action_descriptions(text):
    """Remove action descriptions but keep dialogue content"""
    # Remove \[...\] action descriptions at the start
    text = re.sub(r'^\\\[.*?\\\]\s*', '', text)
    # Also remove regular bracketed actions
    text = re.sub(r'^\[.*?\]\s*', '', text)
    return text.strip()

def main():
    input_file = '广播剧脚本：三千年后的我与AI女友还在吵架.md'
    output_file = '广播剧_正确版.txt'

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    dialogues = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if line contains role marker: **\[角色\]**：
        if '**\\[' in line and ']**' in line and ('：' in line or ':' in line):
            # Extract role name
            start = line.find('[') + 1
            end = line.rfind(']')

            if start > 0 and end > start:
                role_full = line[start:end]

                # Get role name only
                if '：' in role_full:
                    role = role_full.split('：')[0].strip()
                else:
                    role = role_full.strip()

                # Look for dialogue in next lines
                i += 1

                # Skip empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # Get dialogue content
                if i < len(lines):
                    dialogue_line = lines[i].rstrip()

                    # Only remove action descriptions at the start, keep all dialogue content including colons
                    clean_dialogue = clean_action_descriptions(dialogue_line)

                    if clean_dialogue:
                        dialogues.append(f"【{role}】{clean_dialogue}")

        i += 1

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(dialogues))

    print(f"Total: {len(dialogues)} dialogues\n")
    print("Checking problematic dialogues:\n")

    # Find and print the specific dialogues mentioned by user
    for i, d in enumerate(dialogues, 1):
        if '生成结果如下' in d or '套路永远是' in d:
            print(f"{i}. {d}\n")

    print("\nFirst 5 dialogues:")
    for i, d in enumerate(dialogues[:5], 1):
        print(f"{i}. {d}\n")

if __name__ == '__main__':
    main()
