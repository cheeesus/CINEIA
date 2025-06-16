import os

# 设置目标目录
target_dir = r"/data/synthese/CINEIA"

# 设置输出文件路径
output_file = os.path.join(os.getcwd(), "code_description.txt")

# 要排除的目录名集合（不包含路径）
EXCLUDE_DIRS = {'.git', '__pycache__', '.ipynb_checkpoints'}

def generate_directory_tree(start_path, prefix=''):
    tree_lines = []
    files = sorted(os.listdir(start_path))
    for index, name in enumerate(files):
        if name in EXCLUDE_DIRS:
            continue  # 跳过无关目录
        path = os.path.join(start_path, name)
        connector = '└── ' if index == len(files) - 1 else '├── '
        tree_lines.append(f"{prefix}{connector}{name}")
        if os.path.isdir(path):
            extension = '    ' if index == len(files) - 1 else '│   '
            tree_lines.extend(generate_directory_tree(path, prefix + extension))
    return tree_lines

with open(output_file, 'w', encoding='utf-8') as out_f:
    # 1️⃣ 写入目录结构
    out_f.write(f"目录结构（{target_dir}）\n")
    tree_output = generate_directory_tree(target_dir)
    for line in tree_output:
        out_f.write(line + '\n')

    out_f.write("\n\n文件内容如下：\n")

    # 2️⃣ 写入每个 .py / .md / .sh / dockerfile 文件内容（排除 EXCLUDE_DIRS）
    for root, dirs, files in os.walk(target_dir):
        # 修改 dirs 以原地排除不需要遍历的目录（重要）
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".sh") or file == "dockerfile":
                file_path = os.path.join(root, file)
                out_f.write(f"\n===== 文件: {file_path} =====\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        out_f.write(content + "\n")
                except Exception as e:
                    out_f.write(f"读取失败: {e}\n")

print(f"✅ 所有内容已写入：{output_file}")
