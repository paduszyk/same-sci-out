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
