FROM python:3.8-slim
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip install --no-cache .[dev]
