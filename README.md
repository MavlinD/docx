[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-0.1.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://github.com/MavlinD/docx

### Шаблонизатор для файлов __*.docx__ (MS Word)

#### Развертывание (deploy)
```shell
cp template.env .env
# установить нужные значения 
# загрузить в папку public_keys публичный ключ/и сервисов клиентов
# добавить нужные шаблоны в папку templates
docker compose up 
```

#### Авторизация запросов
Основана на использовании [JWT](https://datatracker.ietf.org/doc/html/rfc7519?roistat_visit=181883) завереных на ассиметричных алгоритмах подписей (ES256, PS256, EdDSA и тп.).

##### Для добавления сервиса клиента нужно:
1. [Загрузить публичный ключ сервиса клиента](public_keys/README.md).
2. [Установить требуемые разрешения](template.env).
3. Добавить JWT в нагрузку запроса, в поле token. 

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

[основной пакет](https://docxtpl.readthedocs.io/en/latest/#indices-and-tables)  
