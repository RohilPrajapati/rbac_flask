# Simple RBAC CRUD App using Flask with session based authentication

## TODO (Remaining Works)

- check form validation both client and server side
- manage permission for music and artist
- create artist record when artist role user is created
    - allow artist to access, edit and delete music
- import from CSV
- design simple dashboard


### Latest development branch:
```
feat/artist_crud
```

### Setup process

- sync dependency
```bash
uv sync
```

- create .env file

- setup db: this command will create tables for application
```bash
uv run python -m app.setup_db
```

- to run project
```bash
uv run flask --app app run --debug
```
