FROM python:3.9

WORKDIR /usr/src/app

# Setup
RUN pip install poetry wheel

# Dependencies installation
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install

# Now project files is avaliable
COPY Makefile ./
COPY codstattracker ./codstattracker
COPY tests ./tests

# Lint & test
RUN make lint
RUN make test

# Build package
RUN make build
