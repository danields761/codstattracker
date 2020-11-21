poetry_cmd=poetry
CMD_PREFIX ?= ${poetry_cmd} run
build_artifact_name=dist/build.whl
lint_targets = codstattracker tests migrations
WHEEL_NAME_FILE ?= dist/wheel_name.txt
DB_TYPE ?= sqlite


## Install dependencies
install-deps:
	@${poetry_cmd} install
	@echo Development dependencies installed

## Check code-style
lint:
	@${CMD_PREFIX} flake8 ${lint_targets}
	@${CMD_PREFIX} isort --check ${lint_targets}
	@${CMD_PREFIX} black --check ${lint_targets}

## Coerce code-style
fmt:
	@${CMD_PREFIX} isort ${lint_targets}
	@${CMD_PREFIX} black ${lint_targets}

## Run unit-tests
test:
	@${CMD_PREFIX} pytest .

## Run integration-tests, requires "DB_URI" env variable
int-test:
	@{ \
		set -e; \
		if [ -z $$DB_URI ]; then echo 'Target requires "DB_URI" env variable'; exit 1; fi; \
		${CMD_PREFIX} pytest --use-migrations --test-db-uri $$DB_URI . ; \
  	}

## Generate migrations for "$DB_TYPE" outputting them into "$DB_TYPE_migrations" folder
gen-migrations:
	@mkdir -p ${DB_TYPE}_migrations
	@${CMD_PREFIX} python generate_migrations.py ${DB_TYPE} ${DB_TYPE}_migrations

## Build project into wheel, place it under "dist" folder (may be altered via $DIST_DST).
## Wheel filename can be read from "dist/wheel_name.txt"
build: 
	@{ \
		set -e; \
		tmp_file=$$(mktemp); \
		${poetry_cmd} build -f wheel | tee $$tmp_file; \
		wheel_name=$$(cat $$tmp_file | grep -P -o 'codstattracker[-\d\w.]+'); \
		echo Wheel "$$wheel_name" succesfully built; \
		echo Writing wheel name into ${WHEEL_NAME_FILE} ; \
		echo $$(pwd)/dist/$$wheel_name > ${WHEEL_NAME_FILE}; \
	}
