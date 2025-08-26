FROM python:3.12-slim
RUN pip install --upgrade pip
RUN pip install pytest requests pydantic jmespath lxml deprecated
