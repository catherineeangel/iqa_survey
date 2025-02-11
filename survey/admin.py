from django.contrib import admin
from .models import Participant, Image, ImageRating, FinalSurvey


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "date")  
    search_fields = ("name",)  

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("file_name", "upload_date")  
    search_fields = ("file_name",)  

@admin.register(ImageRating)
class ImageRatingAdmin(admin.ModelAdmin):
    list_display = ("participant", "image", "rating")  
    list_filter = ("rating",)  
    search_fields = ("participant__name", "image__file_name")  

@admin.register(FinalSurvey)
class FinalSurveyAdmin(admin.ModelAdmin):
    list_display = ("participant", "contrast", "sharpness", "colorfulness", "brightness")  
    list_filter = ("contrast", "sharpness", "colorfulness", "brightness")  
    search_fields = ("participant__name",)  
