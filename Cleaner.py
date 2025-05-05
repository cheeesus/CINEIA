import subprocess

def get_git_objects():
    cmd = "git rev-list --objects --all"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, shell=True)
    return result.stdout.strip().split('\n')

def get_object_size(sha):
    cmd = f"git cat-file -s {sha}"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, shell=True)
    return int(result.stdout.strip())

objects = get_git_objects()
size_list = []

for obj in objects:
    parts = obj.strip().split()
    if len(parts) == 2:
        sha, path = parts
        size = get_object_size(sha)
        size_list.append((size, path))

size_list.sort(reverse=True)

for size, path in size_list[:20]:
    print(f"{size / (1024*1024):.2f} MB\t{path}")
