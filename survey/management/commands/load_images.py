import os
from django.core.management.base import BaseCommand
from survey.models import Image 
from django.conf import settings


class Command(BaseCommand):
    help = "Load images from 'static/images' into the Image model in order"

    def handle(self, *args, **kwargs):
        image_folder = os.path.join(settings.BASE_DIR, "static", "images")

        if not os.path.exists(image_folder):
            self.stdout.write(self.style.ERROR(f"Folder not found: {image_folder}"))
            return

        # Sort filenames numerically/alphabetically
        image_files = sorted([
            f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        if not image_files:
            self.stdout.write(self.style.WARNING("No image files found in folder."))
            return

        for index, image_file in enumerate(image_files):
            if not Image.objects.filter(file_name=image_file).exists():
                Image.objects.create(file_name=image_file)
                self.stdout.write(self.style.SUCCESS(f"{index+1:04d}: Added {image_file}"))
            else:
                self.stdout.write(self.style.WARNING(f"{index+1:04d}: Skipped (Already Exists): {image_file}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Image Loading Complete!"))