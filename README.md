# Obscene filter 
 
Demo example with django-admin and REST interface

## Deploy

### Using make
```make simple_start``` - start in one command using docker

### Envs

```
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DJANGO_SUPERUSER_PASSWORD=admin
SUSPICIOUS_WORDS_CHECK=
CHATGPT_API_KEY=
CHATGPT_BASE_URL=
```

SUSPICIOUS_WORDS_CHECK=True if you want to use chatpgt for filling obscene words dictionary

### Urls
* REST api - [ninja docs](http://localhost:8000/api/docs)
* Admin panel - [django admin](http://localhost:8000/admin)
