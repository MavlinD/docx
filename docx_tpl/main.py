from pprint import pprint

from docxtpl import DocxTemplate
import argparse
import pathlib

from config import Config


def main():
    parser = argparse.ArgumentParser(description="Template engine for docx")
    parser.add_argument("--payload", type=str, help="Input dir for videos")
    parser.add_argument("filename", type=str, help="Имя сохраняемого файла")
    args = parser.parse_args()
    print(args.payload)
    BASE_DIR = pathlib.Path().resolve().parent
    doc = DocxTemplate("templates/my_word_template.docx")
    context = {"username": "Васян Хмурый", "place": "Кемерово"}
    doc.render(context)

    # p = pathlib.Path(__file__)
    # print(p)
    # print(pathlib.Path().cwd())
    # pprint(pathlib.Path().resolve().parent)
    # pprint(pathlib.Path().parent)
    # print(pathlib.Path().parent.absolute())
    doc.save(BASE_DIR.joinpath(f"{Config.DOWNLOADS_DIR}/{args.filename}.docx"))


if __name__ == "__main__":
    main()
