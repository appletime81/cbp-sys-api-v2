from docxtpl import DocxTemplate


def convert_arabic_numerals_to_chinese_numerals(number: str):
    chinese_numerals = {
        "0": "\u3007",
        "1": "一",
        "2": "二",
        "3": "三",
        "4": "四",
        "5": "五",
        "6": "六",
        "7": "七",
        "8": "八",
        "9": "九",
        ".": "．",
        ",": "、",
    }

    # print(number)
    result = ""
    for i in number:
        if i.isdigit():
            print(i)
            result += chinese_numerals[str(i)]
        elif i == ".":
            result += chinese_numerals["."]
        elif i == ",":
            result += chinese_numerals[","]
    return result


# chinese_numbers
# 208,294.52
print(convert_arabic_numerals_to_chinese_numerals("208,294.52"))
context = {
    "chinese_numbers": convert_arabic_numerals_to_chinese_numerals("208,294.52"),
}
doc = DocxTemplate("chinese_numbers.docx")
doc.render(context)
doc.save("chinese_numbers_output.docx")
