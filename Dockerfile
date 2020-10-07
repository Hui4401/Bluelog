FROM python:3.8

LABEL maintainer="Assassin"

WORKDIR /root/Bluelog

COPY . .

RUN pip install -i https://pypi.douban.com/simple -r requirements.txt \
        && pip install -i https://pypi.douban.com/simple gunicorn \
        && flask init -u root -p 111

CMD gunicorn -w 6 -b 0.0.0.0:8000 wsgi:app
