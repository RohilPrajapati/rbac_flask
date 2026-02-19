import click
from app.models import register_user, get_user_with_email
from app.utils.exceptions import ValidationError
from app.services.auth import validate_registration_field


def register_cli_commands(app):

    @app.cli.command("create-super-admin")
    def create_super_admin():
        """Create a Super Admin user from CLI"""

        data = {}

        def prompt_and_validate(field_name, prompt_text, hide_input=False):
            while True:
                value = click.prompt(prompt_text, hide_input=hide_input)

                try:
                    validate_registration_field(field_name, value, data)
                    return value

                except ValidationError as ve:
                    for field, msg in ve.errors.items():
                        click.echo(click.style(f"{msg}", fg="red"))

        data["first_name"] = prompt_and_validate("first_name", "First name")
        data["last_name"] = prompt_and_validate("last_name", "Last name")
        data["email"] = prompt_and_validate("email", "Email")

        while True:
            password = click.prompt("Password", hide_input=True)
            c_password = click.prompt("Confirm Password", hide_input=True)

            try:
                validate_registration_field("password", password, data)

                validate_registration_field(
                    "c_password",
                    c_password,
                    {**data, "password": password},
                )

                data["password"] = password
                data["c_password"] = c_password
                break

            except ValidationError as ve:
                errors = ve.args[0]
                for field, msg in errors.items():
                    click.echo(
                        click.style(
                            f"{field.replace('_', ' ').title()}: {msg}",
                            fg="red",
                        )
                    )

        data["phone"] = prompt_and_validate("phone", "Phone")
        data["dob"] = prompt_and_validate("dob", "Date of birth (YYYY-MM-DD)")
        data["gender"] = prompt_and_validate("gender", "Gender ('m','f','o')")
        data["address"] = prompt_and_validate("address", "Address")

        data["role"] = "super_admin"

        try:
            user_id = register_user(data)

            click.echo(
                click.style(
                    f"Super Admin created successfully! ID: {user_id}",
                    fg="green",
                )
            )

        except ValidationError as ve:
            errors = ve.args[0]
            for field, msg in errors.items():
                click.echo(
                    click.style(
                        f"{field.replace('_', ' ').title()}: {msg}",
                        fg="red",
                    )
                )

        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))


def register_default_admin(app):

    @app.cli.command("create-default-admin")
    def create_default_admin():
        """Create a default super-admin user automatically."""

        default_email = "admin@admin.com"

        # Check if user already exists
        if get_user_with_email(default_email):
            print(f"Super-admin with email {default_email} already exists.")
            return

        data = {
            "first_name": "Super",
            "last_name": "Admin",
            "email": default_email,
            "password": "admin123",
            "c_password": "admin123",
            "phone": "9800000000",
            "dob": "2000-01-01",
            "gender": "m",
            "address": "Nepal",
            "role": "super_admin",
        }

        try:
            user_id = register_user(data)
            print(f"Super-admin created successfully! ID: {user_id}")
        except Exception as e:
            print(f"Error creating super-admin: {e}")
