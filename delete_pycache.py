import os


def delete_pycache():
    current_path = os.getcwd()
    for root, dirs, files in os.walk(current_path):
        for dir in dirs:
            if "__pycache__" == dir:
                os.system(f"rm -rf {os.path.join(root, dir)}")
                print(f"{os.path.join(root, dir)} is deleted.")


if __name__ == "__main__":
    delete_pycache()
