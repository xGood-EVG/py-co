import os
import sys
import zlib

def get_branches(repo_path):
    refs_path = os.path.join(repo_path, ".git", "refs", "heads")
    if not os.path.exists(refs_path):
        print("Such directory does not exist")
        return
    for branch in os.listdir(refs_path):
        print(branch)


def get_last_commit(repo_path, branch_name):
    branch_ref_path = os.path.join(repo_path, ".git", "refs", "heads", branch_name)
    
    if os.path.exists(branch_ref_path):
        with open(branch_ref_path, "r") as f:
            commit_hash = f.read().strip()
        return commit_hash


def get_last_commit_info(repo_path, branch_name):
    commit_hash = get_last_commit(repo_path, branch_name)
    return read_git_object(repo_path, commit_hash)


def get_tree_info(repo_path, branch_name):
    commit_content = get_last_commit_info(repo_path, branch_name)

    for line in commit_content.splitlines():
        if line.startswith("tree "):
            tree_hash = line.split(" ")[1]
            break

    return read_git_object(repo_path, tree_hash)


def read_git_object(repo_path, object_hash):
    obj_path = os.path.join(repo_path, ".git", "objects", object_hash[:2], object_hash[2:])
    if not os.path.exists(obj_path):
        return f"Объект {object_hash} не найден."
    with open(obj_path, "rb") as f:
        obj = zlib.decompress(f.read())
        header, _, body = obj.partition(b'\x00')
        kind, size = header.split()

    output = ""
    if kind == b'tree':
        i = 0
        while i < len(body):
            mode_end = body.find(b' ', i)
            mode = body[i:mode_end].decode()

            name_end = body.find(b'\x00', mode_end)
            name = body[mode_end + 1:name_end].decode()

            sha = body[name_end + 1:name_end + 21]
            obj_hash = sha.hex()

            obj_path = os.path.join(repo_path, ".git", "objects", obj_hash[:2], obj_hash[2:])
            with open(obj_path, "rb") as obj_file:
                obj_type = zlib.decompress(obj_file.read()).split(b' ')[0].decode()

            output += f"{obj_type:<5} {obj_hash} {name}\n"
            i = name_end + 21

        return output.strip()

    elif kind == b'commit':
        return body.decode(errors='ignore')


def get_parent_commit(commit_body):
    for line in commit_body.splitlines():
        if line.startswith("parent "):
            return line.split()[1]
    return None


def get_commit_tree_hash(commit_body):
    for line in commit_body.splitlines():
        if line.startswith("tree "):
            return line.split()[1]
    return None


def print_commit_history(repo_path, branch_name):
    commit_hash = get_last_commit(repo_path, branch_name)

    while commit_hash:
        commit_body = read_git_object(repo_path, commit_hash)

        tree_hash = get_commit_tree_hash(commit_body)
        print(f"TREE for commit {commit_hash}")
        print(read_git_object(repo_path, tree_hash))
        print()

        commit_hash = get_parent_commit(commit_body)


repo_path = sys.argv[1]
if len(sys.argv) == 2:
    get_branches(repo_path)
elif len(sys.argv) == 3:
    branch_name = sys.argv[2]
    print("Choose option")
    print(" 1 - Get last commit info\n", "2 - Get tree from last commit\n", "3 - Get history")
    
    option = input()
    match option:
        case "1":
            print(get_last_commit_info(repo_path, branch_name).rstrip())
        case "2":
            print(get_tree_info(repo_path, branch_name))
        case "3":
            print_commit_history(repo_path, branch_name)