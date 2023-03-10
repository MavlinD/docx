[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-0.1.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://github.com/MavlinD/docx

### Шаблонизатор для docx (MS Word)

[основной пакет](https://docxtpl.readthedocs.io/en/latest/#indices-and-tables)

#### Manual deploy
```shell
cp template.env .env
# установить нужные значения
# загрузить в папку public_keys публичный ключ/и сервисов клиентов
# добавить нужные шаблоны в папку templates
docker compose up 
```
#### Tests
```shell
# запустить все тесты
pytest -x  
# мониторинг изменений
ptw -- 5 mon
# где 5 - уровень логирования 
```
