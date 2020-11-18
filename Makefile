poetry_cmd=poetry
cmd_prefix=${poetry_cmd} run
build_artifact_name=dist/build.whl
WHEEL_NAME_FILE ?= dist/wheel_name.txt
DB_TYPE ?= sqlite

install-base:
	@pip install poetry

install-dev:
	@${poetry_cmd} install > /dev/null
	@echo Development dependencies installed

lint:
	@${cmd_prefix} flake8 codstattracker tests
	@${cmd_prefix} isort --check .
	@${cmd_prefix} black --check .

fmt:
	@${cmd_prefix} isort .
	@${cmd_prefix} black .

test:
	@${cmd_prefix} pytest .

gen-migrations:
	@mkdir -p ${DB_TYPE}_migrations
	@${cmd_prefix} python generate_migrations.py ${DB_TYPE} ${DB_TYPE}_migrations

build:
	@{ \
  	set -e; \
  	tmp_file=$$(mktemp); \
  	${poetry_cmd} build -f wheel | tee $$tmp_file; \
	wheel_name=$$(cat $$tmp_file | grep -P -o 'codstattracker[-\d\w.]+'); \
	echo Wheel "$$wheel_name" succesfully built; \
	echo Writing wheel name into ${WHEEL_NAME_FILE} ; \
	echo $$wheel_name > ${WHEEL_NAME_FILE}; \
	}
