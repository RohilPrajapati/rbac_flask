# Simple RBAC CRUD App using Flask with session based authentication

### setup process

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
