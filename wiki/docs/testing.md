#### Tests
```shell
# создать виртуальное окружение
poetry shell
# установить все пакеты
poetry i
# запустить все тесты
pytest -x  
# мониторинг изменений
ptw -- 5 mon
# где 5 - уровень логирования 
```
где 5 - [уровень логирования](https://docs.python.org/3/library/logging.html#logging-levels) 

{% 
include 'links.md'
rewrite-relative-urls=false
%}
