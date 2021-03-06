from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import signals
from django.dispatch import receiver

from PIL import Image

from .models import USER_ICON_SIZE, USER_PHOTO_SIZE, User


@receiver(signals.post_save, sender=User)
def post_process_user_photo(sender, instance, **kwargs):
    """Post process the user photo."""
    if not instance.photo:
        return None

    with Image.open(instance.photo.path) as photo:
        # Determine the cropping area coordinates depending on the photo shape
        width, height = photo.size
        if height > width:  # portrait
            box = (0, int((height - width) / 2), width, int((height + width) / 2))
        elif height < width:  # landscape
            box = (int((width - height) / 2), 0, int((width + height) / 2), height)
        else:
            box = (0, 0, width, height)

        # Crop & resize, then overwrite the original photo
        with photo.crop(box).resize(USER_PHOTO_SIZE) as new_photo:
            new_photo.save(instance.photo.path)


@receiver(signals.post_save, sender=User)
def create_user_icon(sender, instance, **kwargs):
    """Create and save the user icon."""
    if instance.photo:
        if instance.icon:
            return None

        with Image.open(instance.photo.path) as photo:
            icon = photo.resize(size=USER_ICON_SIZE)

            with BytesIO() as icon_file:
                icon.save(icon_file, format=photo.format)
                icon_file.seek(0)

                if not instance.icon:
                    instance.icon.save(
                        instance.photo.name,  # only to retrieve the file extension
                        ContentFile(icon_file.read()),
                        save=True,
                    )
                else:
                    # Note that instance has been just saved within post_save
                    # signal. Therefore, do nothing if the icon field has been
                    # already populated. Otherwise, RecursionError is raised.
                    pass
    else:
        # If there is no photo but icon, remove the icon file as well
        if instance.icon:
            instance.icon.delete(save=True)
