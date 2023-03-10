[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-0.1.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://github.com/MavlinD/docx

### Шаблонизатор для docx (MS Word)

[основной пакет](https://docxtpl.readthedocs.io/en/latest/#indices-and-tables)

```shell
# сборка образа
d build -t docx-tpl .
# запуск с параметрами
d run --rm docx-tpl python docx/main.py tst
```
