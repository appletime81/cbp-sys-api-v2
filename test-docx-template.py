from docxtpl import *

docx_template = DocxTemplate("test-template.docx")
context = {
    'Test1': '1',
    'Test2': '2',
    'Test3': '3',
    'Test4': '\f',
    'Test5': '5',
    'Test6': '6',
    'Test7': '7',

}

docx_template.render(context, autoescape=True)
docx_template.save("test-template-output.docx")
