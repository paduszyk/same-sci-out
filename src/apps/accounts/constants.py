import os

from django.utils.translation import gettext_lazy as _

# User model `sex` field choices

SEX_MALE = "M"
SEX_FEMALE = "F"
SEX_UNKNOWN = "U"

SEX_CHOICES = [
    (SEX_UNKNOWN, _("nie chcę podawać")),
    (SEX_FEMALE, _("kobieta")),
    (SEX_MALE, _("mężczyzna")),
]

SEX_DEFAULT = SEX_UNKNOWN


# User `photo` and `icon` fields dirs and sizes
# TODO Find a way to not hardcode paths' dir names  # NOQA

USER_PHOTO_DIR = "photo"
USER_PHOTO_PATH = os.path.join("accounts", "user", USER_PHOTO_DIR)
USER_PHOTO_SIZE = (512, 512)  # px

USER_ICON_DIR = "icon"
USER_ICON_PATH = os.path.join("accounts", "user", USER_ICON_DIR)
USER_ICON_SIZE = (64, 64)  # px
