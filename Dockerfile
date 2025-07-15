FROM python:3.12-slim



WORKDIR /app
COPY pyproject.toml .
COPY imdbinfo ./imdbinfo

#RUN pip install --upgrade pip
RUN pip install -e .
