FROM python:3.8-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod 1777 /tmp
RUN apt-get update && apt-get --allow-unauthenticated install -y netcat-traditional

RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app

ENV APP_HOME=/home/app/web

RUN mkdir -p $APP_HOME/staticfiles

WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . $APP_HOME
RUN chown -R app:app $APP_HOME


ENTRYPOINT ["/home/app/web/entrypoint.sh"]
