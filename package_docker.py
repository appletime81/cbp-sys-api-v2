import os


# Step1. -> Create a folder called cbps-docker-folder
os.mkdir("cbps-docker-folder")

# Step2. -> put ['main.py', 'crud.py', 'get_db.py', 'schemas.py', 'dbinfo.ini', ''Dockerfile, 'userinfo.ini', 'requirements.txt'] into cbps-docker-folder
os.system("cp main.py crud.py get_db.py schemas.py dbinfo.ini Dockerfile userinfo.ini requirements.txt cbps-docker-folder")

# Step2. -> put folders ['database', 'images', 'service', 'utils', 'templates'] into cbps-docker-folder
os.system("cp -r database images service utils templates cbps-docker-folder")