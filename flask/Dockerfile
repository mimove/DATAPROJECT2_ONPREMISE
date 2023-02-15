FROM python:3.8.5-alpine
COPY . /app
WORKDIR /app
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN pip install -r requirements.txt
EXPOSE 5000
# ENTRYPOINT ["python"]
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
