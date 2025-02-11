from django.db import models
import random

class Participant(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

class Image(models.Model):
    file_name = models.CharField(max_length=255)  
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

class ImageRating(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Scale 1-5

    def __str__(self):
        return f"{self.participant.name} - {self.image.file_name} - {self.rating}"

class FinalSurvey(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    contrast = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)], verbose_name="Contrast Importance")
    sharpness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)], verbose_name="Sharpness Importance")
    colorfulness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)], verbose_name="Colorfulness Importance")
    brightness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 5)], verbose_name="Brightness Importance")
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Final Survey - {self.participant.name}"
