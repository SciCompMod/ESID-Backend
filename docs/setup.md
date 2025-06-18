# pandemos-interface
Source code repository for pandemos APIs.

## Deployment
### Setup the Project
1. Clone the project:
```
git clone git@github.com:DLR-SC/ESID-Backend.git
```

2. Go to `api` directory.
```
cd api/
```

3. Create `docker-env` and modify the file as needed.
```
cp .docker-env.template .docker-env
```

4. run docker compose:
```
docker compose up --build -d
```
> [!NOTE]  
> In older docker compose versions you may need to provide the .env file because the file is not recognized in the `docker-compose.yml`  
> In this case add `--env-file .docker-env`:  
> ```
> docker compose --env-file .docker-env up --build -d
> ```
> The other commands in theory need the env reference too, but should work without despite any warnings.

5. Perform database migrations (Create tables - on initial run)   
- Generate code for migration:
```
docker compose exec api alembic revision --autogenerate -m "Create all tables"
```
- Execute the migration
```
docker compose exec api alembic upgrade head
```


## API
Goto http://localhost:8000/

API docs can be found at:
http://localhost:8000/docs


# Developer Pre-requisites
## Project Setup
### Docker
Follow steps 1-3 from Deployment - Setup the Project.

You can use `docker compose logs -f` to get a feed of the container logs.

`docker compose logs -f api db` to only see logs for the api & db containers.

You can attach to the containers to check their runtime environment with `docker exec -it <container-name> bash`.

watchgod will automatically restart the docker-ized Application with each code change.

## Development
In order to commit changes, the pre-commit package is now a pre-requisite.
Pre-commit hooks ensure a higher code-quality and readability. 

To install pre-commit, execute the following command: 
```
pip install pre-commit
```
