import os


def main():
    # remove backend folder
    os.system("rm -rf backend")

    # mkdir
    os.mkdir("backend")

    # copy images folder to backend
    os.system("cp -r images backend")

    # copy templates folder to backend
    os.system("cp -r templates backend")

    # copy database folder to backend
    os.system("cp -r database backend")

    # copy service folder to backend
    os.system("cp -r service backend")

    # copy utils folder to backend
    os.system("cp -r utils backend")

    # copy main.py to backend
    os.system("cp main.py backend")

    # copy get_db.py to backend
    os.system("cp get_db.py backend")

    # copy schemas.py to backend
    os.system("cp schemas.py backend")

    # copy crud.py to backend
    os.system("cp crud.py backend")

    # copy delete_pycache.py to backend
    os.system("cp delete_pycache.py backend")

    # copy start.sh to backend
    os.system("cp start.sh backend")

    # copy *.ini to backend
    os.system("cp *.ini backend")


if __name__ == "__main__":
    main()
