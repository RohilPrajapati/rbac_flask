# Simple RBAC CRUD App using Flask with session based authentication

## TODO (Remaining Works)

- Security and Optimization
    - setup database connection pool
    - add CSRF token to the form and verify it to protect against CSRF attacks.
- implement test cases for auth and permission in route and crud
- Mobile Responsive


### Setup Process

- sync dependency
```bash
uv sync
```

- create .env file using example.env

- setup db: this command will create tables for application
```bash
uv run python -m app.setup_db
```

- create super-admin: this command will create super-admin user
```bash
uv run flask create-super-admin
```

- to run project
```bash
uv run flask --app app run --debug
```

### Setup Run using Docker

- create .docker.env file with the help of example.env

- build the project
```bash
docker compose build --no-cache
```
- run the project
```bash
docker compose up    
```


### Project Structure

```bash
app/
├── routes/                     # include all the route for the folder
│   ├── __init__.py
│   ├── artist.py
│   ├── auth.py
│   ├── dashboard.py
│   ├── music.py
│   └── user.py
├── services/                   # include validation for tables     
│   ├── __init__.py
│   ├── artist.py
│   ├── auth.py
│   └── music.py
├── static/                     # include static file like js and css
│   ├── main.js
│   └── style.css
├── templates/                  # include jinja template
│   ├── artist/
│   ├── auth/
│   ├── components/
│   ├── music/
│   ├── user/
│   ├── 404.j2
│   ├── base.j2
│   └── dashboard.j2
└── utils/                      # include project utils for auth and Validator class
│   ├──
│   ├── decorators.py
│   ├── exceptions.py
│   └── validator.py
├── __init__.py
├── config.py
├── db.py
├── models.py
└── setup_db.py
.env                            # copy example.env and update with own data
.gitignore
.python-version
example.env
pyproject.toml                  # install dependecy using uv
requirements.txt                # install dependency using pip
```


## ScreenShot

- Registration form with validation error
![Registration Form with Validation Error](screenshot/registration_form_with_validation_error.png)
- login form
![Login Form](screenshot/login_form.png)
- User list
![User List](screenshot/user_list.png)
- User Detail
![User Detail](screenshot/user_detail.png)
- User add form
![User Add Form](screenshot/user_add_form.png)
- Artist list
![Artist List](screenshot/artist_list.png)
- Artist detail
![Artist Detail](screenshot/artist_detail_with_music_list.png)