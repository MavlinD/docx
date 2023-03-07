FROM python:3.11

ARG USERNAME=appuser
ENV APP_HOME=/home/$USERNAME

ENV ACCEPT_EULA=Y \
    LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8 \
    PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # poetry: https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.3.2 \
    # make poetry install to this location
    POETRY_HOME="$APP_HOME/poetry" \
    # make poetry create the virtual environment in the project's root
    POETRY_VIRTUALENVS_CREATE=false \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths: this is where our requirements + virtual environment will live
    PYSETUP_PATH="$APP_HOME/pysetup" \
    VENV_PATH="$APP_HOME/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# set locale to datetime
RUN apt-get update && \
    apt-get install -y tree less locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    # добавим редактор внутрь образа - для отладки =
    curl https://getmic.ro | bash && \
    mv micro /usr/bin && \
    useradd --create-home $USERNAME && \
	usermod -aG sudo $USERNAME && \
	echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
	chmod 666 /etc/environment

# add poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    mkdir -p static && mkdir -p src

WORKDIR $APP_HOME/src

COPY . .
#COPY pyproject.toml .
#COPY poetry.lock .
COPY .bashrc $APP_HOME
RUN poetry install && \
    chmod a+rwx -R . && \
    chmod a+rwx -R /usr/local/lib/python3.11
#    chmod a+rwx -R "/usr/local/lib/python${PYTHON_VER}"

USER $USERNAME
# modify path variable
ENV PATH="$APP_HOME/.local/bin:$PATH"

#COPY docx_tpl /home/appuser/src
#COPY . /home/appuser/src
#COPY
CMD sh entrypoint.sh
