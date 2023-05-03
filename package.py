import shutil
import subprocess
import os
import re


def main():
    # remove backend folder
    shutil.rmtree("backend", ignore_errors=True)

    # create backend folder
    os.mkdir("backend")

    # copy required folders and files to backend
    dirs_to_copy = ["images", "templates", "database", "service", "utils"]
    for dir in dirs_to_copy:
        shutil.copytree(dir, f"backend/{dir}")

    files_to_copy = [
        "main.py",
        "get_db.py",
        "schemas.py",
        "crud.py",
        "delete_pycache.py",
        "start.sh",
    ]
    for file in files_to_copy:
        shutil.copy(file, "backend")

    subprocess.run(["cp", "./dbinfo.ini", "./backend"], check=True)
    subprocess.run(["cp", "./userinfo.ini", "./backend"], check=True)

    with open("./backend/database/engine.py", "r") as f:
        # read all content
        content = f.read()

    res = re.search(r'section = "\S+"', content).group()
    findTargetStr = res.split("=")[1].replace('"', "").strip()

    targetStr = "aws"  # database name
    content = content.replace(findTargetStr, targetStr)

    with open("./backend/database/engine.py", "w") as f:
        f.write(content)

    os.system("cd ./backend && tar -zcvf ./backend.tar.gz .")


if __name__ == "__main__":
    main()
