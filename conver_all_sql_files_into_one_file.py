import os


def main(fileName):
    files = os.listdir(f"./{fileName}")
    newLines = []
    for file in files:
        with open(f"./{fileName}/{file}", "r") as fp:
            lines = fp.readlines()
        newLines += lines
    with open(f"./{fileName}/output.sql", "w") as fout:
        fout.writelines(newLines)


if __name__ == "__main__":
    fileName = "AWS_DB_Backup/20230706"
    main(fileName)
