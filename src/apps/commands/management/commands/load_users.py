from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import IntegrityError

from apps.accounts.constants import SEX_DEFAULT

import pandas as pd

# Get the project's User model

User = get_user_model()


# Define the fields of the User model to be loaded.

# Each name is given a string (a field name) or 2-tuple. If the latter, first element is
# the field name, while the second is the default value replacing NaN values in Pandas
# dataframe.

USER_FIELDS = [
    field if isinstance(field, tuple) else (field, None)
    for field in [
        # Define the field here
        "id",
        "username",
        "password",
        ("first_name", ""),
        ("last_name", ""),
        ("sex", SEX_DEFAULT),
        ("email", ""),
        ("is_staff", False),
        ("is_superuser", False),
    ]
]

FIELD_NAMES, FIELD_DEFAULTS = zip(*USER_FIELDS)

if any(
    name not in [field.name for field in User._meta.concrete_fields]
    for name in FIELD_NAMES
):
    raise ValueError("Invalid field name(s) found in 'USER_FIELDS' setting.")


class Command(BaseCommand):
    """A command for bulk creating/updating the User objects.

    The data for the users to be inserted into database are taken from
    the Excel workbook by using Pandas dataframes.
    """

    help = (
        "Creates or updates users based on the data saved in "
        "the Microsoft Excel workbook."
    )

    def add_arguments(self, parser):
        """Define the command arguments."""
        parser.add_argument(
            "workbook",
            type=str,
            help="Path to the user data Microsoft Excel workbook.",
        )

        user_label = User._meta.label_lower

        parser.add_argument(
            "-s",
            "--sheet",
            nargs=1,
            type=str,
            required=False,
            default=user_label,
            help=(
                "Name of the sheet containing the user data. "
                "Default for the current project is '{}'.".format(user_label)
            ),
        )

    def handle(self, *args, **options):
        """Define what the command does."""
        # Read the arguments
        workbook = options["workbook"]
        sheet = options["sheet"]

        # Check if the sheet with a specified name is saved in the workbook
        if sheet not in pd.ExcelFile(workbook).sheet_names:
            raise ValueError(
                "Sheet '{}' not found in the workbook '{}'.".format(
                    sheet,
                    workbook,
                )
            )

        # Read users data the sheet from the workbook
        users = pd.read_excel(workbook, sheet_name=sheet, dtype="object")

        # Extract only the requested columns
        try:
            users = users[[*FIELD_NAMES]]
        except KeyError:
            raise KeyError(
                "The following columns are missing in the data sheet "
                "'{}' of workbook '{}': {}.".format(
                    sheet,
                    workbook,
                    ", ".join([field for field in FIELD_NAMES if field not in users]),
                )
            )

        # Required fields, i.e. those with default other than None
        required_fields = [
            name
            for name, default in zip(FIELD_NAMES, FIELD_DEFAULTS)
            if default is not None and default != ""
        ]

        # Username and password are the required fields for each user
        if users[required_fields].isnull().values.any():
            raise ValueError(
                "The following fields has to be specified for "
                "all the users: {}.".format(", ".join(required_fields))
            )

        # Handle NaN or empty values in the remaining columns
        for name, default in zip(FIELD_NAMES, FIELD_DEFAULTS):
            if default is not None and name not in required_fields:
                users[name] = users[name].fillna(default)

        # Create and/or update the users
        for _, user in users.iterrows():
            try:
                User.objects.create_user(**user.to_dict())
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR(
                        (
                            "DB integrity issues occurred when creating user '{}'."
                        ).format(user["username"])
                    )
                )
            else:
                if options["verbosity"] > 1:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "User '{}' successfully created.".format(user["username"])
                        )
                    )
