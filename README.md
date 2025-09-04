# video-experiment

## Installing frontend dependencies

- Install javascript dependencies
```npm install```
- Compile javascript
```npm run dev```
- Compile css
```npm run sass```

## Install with Docker

Clone the git repo to your local machine:
```git clone https://github.com/AmericanPhilosophicalSociety/video-experiment.git```

Create the environment files, editing values as you see fit.

In a production environment, you **must** add a secure secret key and change the username and password for the database.
```
cd video-experiment  
cp .env.prod_example .env.prod  
cp .env.prod.db_example .env.prod.db  
```

Build the Docker containers:

```
docker compose build
docker compose up -d
```

Run Django-specific commands:
```
docker compose exec web python manage.py migrate --noinput
docker compsoe exec web python manage.py collectstatic --noinput --clear
```
