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

# Lint & test
RUN poetry run black --check codstattracker
RUN poetry run isort --check codstattracker

# Copy test files and lint them
COPY tests ./tests
RUN poetry run black --check tests
RUN poetry run isort --check tests

# Run tests
RUN make test

# Build package
RUN make build

# Main command just says that built wheel avaliable at particular location
CMD sh -c 'echo Built wheel avaliable at dist/$(cat dist/wheel_name.txt)'
