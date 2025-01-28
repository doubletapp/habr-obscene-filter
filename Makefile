all: build down up

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

psql:
	docker exec -it obscene_filter__db psql -U postgres

dev:
	docker-compose run --rm --volume=${PWD}/src:/src --publish 8000:8000 app bash -c 'gunicorn -w 5 --bind :8000 --limit-request-line 8190 config.wsgi:application --reload'

makemigrations:
	docker-compose run --volume=${PWD}/src:/src app bash -c '/wait && python manage.py makemigrations'
	sudo chown -R ${USER} src/*/migrations/

migrate:
	docker-compose run app bash -c '/wait && python manage.py migrate $(if $m, api $m,)'

collectstatic:
	docker-compose run app bash -c '/wait && python manage.py collectstatic --no-input'

shell:
	docker-compose run app python manage.py shell

createsuperuser:
	docker-compose run app python manage.py createsuperuser --noinput --username admin --email admin@example.com

# $m [marks]
# $k [keyword expressions]
# $o [other params in pytest notation]
dev_test:
	docker-compose run --volume=${PWD}/src:/src --rm app pytest $(if $m, -m $m)  $(if $k, -k $k) $o

poetry_lock:
	docker-compose run --rm --no-deps --volume=${PWD}:${PWD} --workdir=${PWD} app poetry lock --no-update
	sudo chown -R ${USER} ./poetry.lock

test:
	docker-compose run app pytest

simple_start: build  up  migrate  createsuperuser  collectstatic

