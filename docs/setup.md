# pandemos-interface
Source code repository for pandemos APIs.

## Deployment
### Setup the Project
1. Clone the project:
```
git clone git@github.com:DLR-SC/ESID-Backend.git
```
2. Go to `api` directory.
3. Create `docker-env` and run docker compose:
```
cp .docker-env.template .docker-env
```
```
docker compose up --build -d
```
4. Perform database migrations (Create tables - on initial run)
    
* Generate code for migration

```
docker compose exec api alembic revision --autogenerate -m "Create all tables"
```

* Execute the migration

```
docker compose exec api alembic upgrade head
```

> [!NOTE]  
> In older docker compose versions you may need to provide the .env file in each command (3 & 4) because the file is not recognized in the docker-compose.yml
> in this case add `--env-file .docker-env` directly after `docker compose` and before the rest of the commands

## API
Goto http://localhost:8000

API docs can be found at:
http://localhost:8000/docs


# Developer Pre-requisites
## Project Setup
### Docker
Follow steps 1-3 from Deployment - Setup the Project.
watchgod will automatically restart the docker-ized Application with each code change.

## Development
In order to commit changes, the pre-commit package is now a pre-requisite.
Pre-commit hooks ensure a higher code-quality and readability. 

To install pre-commit, execute the following command: 
```
pip install pre-commit
```
