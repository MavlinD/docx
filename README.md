[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-0.1.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://github.com/MavlinD/docx

### Шаблонизатор для файлов __*.docx__ (MS Word)

----

Запросы на создание файла авторизованы, полученные файлы доступны по ссылке.

#### Развертывание (deploy)
```shell
# скопировать и установить нужные значения
cp template.env .env
# создать нужные папки
mkdir templates downloads authorized_keys 
# загрузить в папку authorized_keys публичный ключ/и сервисов клиентов
# добавить нужные шаблоны в папку templates
docker compose up 
```

#### Авторизация запросов
Основана на использовании [JWT][1] завереных на ассиметричных алгоритмах подписей (ES*, PS*, EdDSA и тп.).


#### Добавления сервиса клиента:
1. [Загрузить публичный ключ сервиса клиента](authorized_keys/README.md).
2. Сервис клиент должен уметь добавлять требуемую аудиенцию в формируемый токен.
3. Добавить [JWT][1] в нагрузку запроса, в поле `token`. 


#### Локальный запуск  
```shell
# создать виртуальное окружение
poetry shell
# установить все пакеты
poetry i
# запустить
python3 src/docx/main.py
```

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

```shell
d run --rm -it --env-file=.env -p 5000:5000 --name=docx docx
d build --build-arg SRC_NAMESPACE='--without dev' -t docx .
```

[1]: https://datatracker.ietf.org/doc/html/rfc7519?roistat_visit=181883 "JWT"

----

[Основной пакет](https://docxtpl.readthedocs.io/en/latest/#indices-and-tables), руководство по работе с шаблонами.    
