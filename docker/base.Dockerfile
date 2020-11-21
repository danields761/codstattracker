FROM python:3.9

WORKDIR /usr/src/codstattracker

# Setup
RUN pip install poetry wheel
RUN poetry config virtualenvs.in-project true

# Dependencies installation
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install

# Now project files is available
COPY Makefile ./
COPY codstattracker ./codstattracker
COPY tests ./tests

# Copy serving files
COPY migrations ./migrations
COPY alembic.ini ./
COPY generate_migrations.py ./

# Lint & test
RUN make lint

# Run tests
RUN make test

# Fix fucking alembic
ENV PYTHONPATH=.
