### Шаблонизатор для docx (MS Word)

[основной пакет](https://docxtpl.readthedocs.io/en/latest/#indices-and-tables)

```shell
# сборка образа
d build -t docx-tpl .
# запуск с параметрами
d run --rm docx-tpl python docx_tpl/main.py tst
```
