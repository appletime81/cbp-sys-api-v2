import shutil
import subprocess
import os
import re


import shutil
import os
import re
import subprocess


def main():
    # remove backend folder and create a new one
    shutil.rmtree("backend", ignore_errors=True)
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
        "dbinfo.ini",
        "userinfo.ini",
    ]
    for file in files_to_copy:
        shutil.copy(file, "backend")

    # read and modify the content of "engine.py"
    with open("./backend/database/engine.py", "r+") as f:
        content = f.read()
        res = re.search(r'section = "\S+"', content).group()
        findTargetStr = res.split("=")[1].replace('"', "").strip()
        targetStr = "aws"  # database name
        content = content.replace(findTargetStr, targetStr)
        f.seek(0)
        f.write(content)
        f.truncate()

    # compress the backend folder
    # subprocess.run(["tar", "-zcvf", "backend.tar.gz", "-C", "backend", "."], check=True)


if __name__ == "__main__":
    main()
