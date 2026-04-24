from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps

from app.core.settings import get_settings


settings = get_settings()
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MEMBER_PHOTO_SIZE = (120, 160)


def _normalize_extension(content_type: str, original_name: str | None) -> str:
    suffix = Path(original_name or 'upload').suffix.lower()
    if content_type == 'image/png':
        return '.png'
    if content_type == 'image/webp':
        return '.webp'
    if suffix in {'.jpg', '.jpeg'}:
        return suffix
    return '.jpg'


def _process_member_photo(content: bytes, extension: str) -> bytes:
    with Image.open(BytesIO(content)) as image:
        normalized = ImageOps.exif_transpose(image).convert('RGB')
        fitted = ImageOps.fit(normalized, MEMBER_PHOTO_SIZE, method=Image.Resampling.LANCZOS)
        buffer = BytesIO()
        output_format = 'PNG' if extension == '.png' else 'WEBP' if extension == '.webp' else 'JPEG'
        save_kwargs = {'quality': 92} if output_format in {'JPEG', 'WEBP'} else {}
        fitted.save(buffer, format=output_format, **save_kwargs)
        return buffer.getvalue()


def save_upload(file: UploadFile, category: str = 'generic') -> dict:
    content = file.file.read()
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError('仅支持 JPG、PNG、WEBP 图片')
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError('图片大小不能超过 5MB')

    upload_dir = settings.resolved_upload_dir
    if category == 'member-photo':
        upload_dir = upload_dir / 'member_photos'
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = _normalize_extension(file.content_type or '', file.filename)
    if category == 'member-photo':
        content = _process_member_photo(content, extension)

    filename = f'{uuid4().hex}{extension}'
    file_path = upload_dir / filename
    file_path.write_bytes(content)

    relative_url = f'/static/uploads/{filename}'
    if category == 'member-photo':
        relative_url = f'/static/uploads/member_photos/{filename}'

    return {
        'filename': filename,
        'content_type': file.content_type,
        'size': len(content),
        'url': relative_url,
    }
