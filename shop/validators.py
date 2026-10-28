from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def validate_product_image(upload):
    if not upload:
        return
    import os
    suffix = os.path.splitext(upload.name)[1].lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError('Only JPEG, PNG and WebP files are allowed.')
    limit = settings.MAX_PRODUCT_IMAGE_MB * 1024 * 1024
    if upload.size > limit:
        raise ValidationError(f'Image must be {settings.MAX_PRODUCT_IMAGE_MB} MB or smaller.')
    if upload.size == 0:
        raise ValidationError('Image cannot be empty.')
    try:
        upload.seek(0)
        with Image.open(upload) as img:
            fmt = img.format
            img.verify()
        if fmt not in ALLOWED_FORMATS:
            raise ValidationError('Unsupported or invalid image content.')
        if fmt == 'JPEG' and suffix not in ('.jpg', '.jpeg'):
            raise ValidationError('File extension does not match JPEG content.')
        if fmt == 'PNG' and suffix != '.png':
            raise ValidationError('File extension does not match PNG content.')
        if fmt == 'WEBP' and suffix != '.webp':
            raise ValidationError('File extension does not match WebP content.')
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise ValidationError('Image is damaged or is not a real image.')
    finally:
        upload.seek(0)
