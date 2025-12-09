FROM python:3.7-slim
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip install  .[dev]
