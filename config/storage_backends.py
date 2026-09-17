"""
2S informatique Plus - Come To Code
Backends de stockage personnalises pour la persistance des fichiers medias.
"""

import os
from cloudinary_storage.storage import MediaCloudinaryStorage


class DynamicMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Stockage Cloudinary unifie et dynamique pour Django 5+.
    
    Par defaut, MediaCloudinaryStorage force RESOURCE_TYPE = 'image'.
    Cette classe detecte automatiquement le type reel du fichier d'apres son extension :
      - 'image' : photos de profil (.jpg, .png, .webp, etc.)
      - 'video' : videos de cours (.mp4, .mov, .mkv, .webm, etc.)
      - 'raw'   : documents pedagogiques PDF (.pdf, .zip, .docx, etc.)

    Cela evite les rejets ou corruptions par Cloudinary lors de l'upload de PDF
    ou de videos, tout en conservant les URLs CDN directes et permanentes.
    """

    IMAGE_EXTENSIONS = {
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'ico', 'tiff', 'tif', 'heic'
    }
    VIDEO_EXTENSIONS = {
        'mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv', '3gp', 'm4v'
    }

    def _get_resource_type(self, name):
        """Determine le type Cloudinary selon l'extension du fichier."""
        _, ext = os.path.splitext(name)
        ext = ext.lower().lstrip('.')
        if ext in self.IMAGE_EXTENSIONS:
            return 'image'
        elif ext in self.VIDEO_EXTENSIONS:
            return 'video'
        return 'raw'
