import json
from pathlib import Path

from django.apps import apps as config
from django.core.management import BaseCommand

import pandas as pd


class Command(BaseCommand):
    """A command for writing Django JSON fixtures from Excel workbook."""

    # NOTE IMPORTANT!!!
    # This command works only if all the project apps are wrapped in the apps package.

    # TODO Fix the hardcoded apps package issue.

    help = "Create JSON Django fixtures from the Microsoft Excel workbook."

    def add_arguments(self, parser):
        """Define the command arguments."""
        parser.add_argument(
            "workbook",
            type=str,
            help="Path to the source MS Excel workbook.",
        )
        parser.add_argument(
            "-a",
            "--apps",
            type=str,
            nargs="+",
            required=True,
            default=[],
            help="Labels of the apps.",
        )

    def handle(self, *args, **options):
        """Define what the command does."""
        Excel2JsonFixtureWriter(
            workbook=options["workbook"],
            apps=options["apps"],
        ).write_fixtures()


class Excel2JsonFixtureWriter:
    """A class to represent a writer for converting database tables saved in
    the MS Excel workbook to the Django fixtures using Pandas dataframes.

    The fixtures returned can the be than easily loaded to the database
    by using the built-in `loaddata` manage.py command.
    """

    def __init__(self, workbook, apps, fixture_dir="fixtures"):
        self._workbook = workbook
        self._fixture_dir = fixture_dir
        self._pk_field = "id"
        self._json_indent = 4

        # All project's apps
        project_apps = [app.label for app in config.get_app_configs()]

        # Account only for the specified apps and their models
        self._apps = []
        for app in apps:
            if app not in project_apps:
                raise ValueError(
                    f"App '{app}' is not installed " f"in the current project."
                )
            if config.get_app_config(app).name.startswith("django."):
                raise ValueError(
                    f"App '{app}' is a built-in Django app. "
                    f"This command does not handle those."
                )
            if not (Path("apps") / app).exists():
                raise ValueError(
                    f"App '{app}' is a 3rd-party app. "
                    f"This command does not handle those."
                )
            self._apps.append(app)

        # All the models of the specified apps
        self._models = [
            model._meta.label_lower
            for model in config.get_models()
            if model._meta.app_label in self._apps
        ]

        # Read and validate the workbook before constructing is completed
        self._read_workbook()
        self._clean_workbook()
        self._check_workbook()

    def __repr__(self):
        return f"{super().__repr__()} reading from '{self._workbook}'"

    def _read_workbook(self):
        """Read the writer's workbook and saves it as a dict of Pandas
        dataframe."""
        self._data = pd.read_excel(
            self._workbook,
            sheet_name=None,
            dtype="object",
        )

    def _clean_workbook(self):
        """Remove all the dataframes/sheets not associated with the project."""
        self._data = {
            key: data for key, data in self._data.items() if key in self._models
        }
        if not self._data:
            raise ValueError(
                f"Workbook '{self._workbook}' does not "
                f"contain sheets matching the project apps."
            )

    def _check_workbook(self):
        """Check if the columns of the writer's dataframes match the models'
        fields."""
        for model, df in self._data.items():
            fields = config.get_model(model)._meta.fields

            # Check for missing columns
            missing = [
                field
                for field in (
                    field.column
                    for field in fields
                    if not field.blank and field.editable
                )
                if field not in df
            ]
            if missing:
                raise ValueError(
                    f"Columns representing the following "
                    f"required fields of the '{model}' model were "
                    f"not found: {', '.join(missing)}."
                )

            # Find invalid columns and drop them
            invalid_columns = [
                column
                for column in df.columns
                if column not in [field.column for field in fields]
            ]
            self._data[model] = df.drop(invalid_columns, axis=1)

    def _write_app_fixtures(self, app_label):
        """Write fixtures for a specified app."""
        if app_label not in self._apps:
            raise ValueError(f"App '{app_label}' is not installed.")

        # Convert workbook data to fixtures
        app_fixtures = []
        for model, df in self._data.items():
            if config.get_app_config(model.split(".")[0]).label != app_label:
                continue

            # Convert Pandas dataframe to list of JSONs
            json_data = json.loads(
                df.to_json(
                    orient="records",
                    date_format="iso",
                ),
            )

            # Save the model fixtures
            model_fixture = []
            for fields in json_data:
                pk = fields.pop(self._pk_field)
                model_fixture.append(
                    {
                        "pk": pk,
                        "model": model,
                        "fields": {
                            key: value
                            for key, value in fields.items()
                            if value is not None
                        },
                    }
                )

            app_fixtures.extend(model_fixture)

        # Write fixtures to JSON file
        if app_fixtures:
            fixture_dir = (Path("apps") / app_label).absolute() / self._fixture_dir
            fixture_dir.mkdir(exist_ok=True, parents=True)

            with open(
                file=fixture_dir / f"{app_label}.json",
                mode="w",
                encoding="utf8",
            ) as fixture_file:
                json.dump(
                    obj=app_fixtures,
                    fp=fixture_file,
                    ensure_ascii=False,
                    indent=self._json_indent,
                )

    def write_fixtures(self, *app_labels):
        """Write fixtures for the specified apps."""
        if not app_labels:
            app_labels = self._apps

        for app_label in app_labels:
            self._write_app_fixtures(app_label)
