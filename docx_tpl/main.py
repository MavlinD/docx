from docxtpl import DocxTemplate


def main():
    doc = DocxTemplate("my_word_template.docx")
    context = {"username": "Васян Хмурый", "place": "Кемерово"}
    doc.render(context)
    doc.save("generated_doc.docx")


if __name__ == "__main__":
    main()
