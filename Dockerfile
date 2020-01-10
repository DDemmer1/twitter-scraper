FROM ubuntu

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8081
ENTRYPOINT [ "python" ]

CMD ["-m", "flask", "run", "--host=0.0.0.0", "--port=8081"]