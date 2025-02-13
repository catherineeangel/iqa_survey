import os
import random
from django.shortcuts import render, redirect
from .models import Participant, Image, ImageRating, FinalSurvey, ParticipantImage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


def start_survey(request):
    if request.method == "POST":
        name = request.POST.get("name")
        
        with transaction.atomic():  
            participant = Participant.objects.create(name=name)
            total_participants = Participant.objects.count()  

        # Fetch all images (already sorted by ID in the database)
        all_images = list(Image.objects.all())

        if not all_images:
            return render(request, "start_survey.html", {"error": "No images available."})

        total_images = len(all_images)
        images_per_participant = 30  # Each participant gets 30 images

        # Determine starting index for this participant
        total_participants = Participant.objects.count()
        start_index = ((total_participants - 1) * images_per_participant) % total_images

        # Select 30 images following the rotation pattern
        selected_images = [
            all_images[(start_index + i) % total_images] for i in range(images_per_participant)
        ]

        # Store selected images in DB
        for img in selected_images:
            ParticipantImage.objects.create(participant=participant, image=img)

        request.session["participant_id"] = participant.id

        return redirect("survey_question")

    return render(request, "start_survey.html")


def survey_question(request):
    participant_id = request.session.get("participant_id")
    if not participant_id:
        return redirect("final_survey")

    participant = Participant.objects.get(id=participant_id)

    # Get image IDs assigned to this participant (sorted by ID to maintain order)
    image_ids = list(
        ParticipantImage.objects.filter(participant=participant)
        .order_by("image__id")  # Ensure order consistency
        .values_list("image__id", flat=True)
    )

    total_images = len(image_ids)

    # Ensure index is in a valid range
    if participant.current_index >= total_images:
        return redirect("final_survey")

    # Get current image
    image = Image.objects.get(id=image_ids[participant.current_index])
    existing_rating = ImageRating.objects.filter(participant=participant, image=image).first()

    image_path = f"/static/images/{image}"
    if request.method == "POST":
        action = request.POST.get("action")
        rating_value = request.POST.get("rating")

        if action in ["next", "finish"] and not rating_value:
            return render(request, "survey_question.html", {
                "image_path": image_path,
                "index": participant.current_index + 1,
                "total": total_images,
                "can_go_prev": participant.current_index > 0,
                "can_go_next": participant.current_index < total_images - 1,
                "existing_rating": existing_rating.rating if existing_rating else None,
                "error": "Please select a rating before proceeding."
            })

        if rating_value:
            if existing_rating:
                existing_rating.rating = int(rating_value)
                existing_rating.save()
            else:
                ImageRating.objects.create(participant=participant, image=image, rating=int(rating_value))

        # Update participant progress in DB instead of session
        if action == "next" and participant.current_index < total_images - 1:
            participant.current_index += 1
            participant.save(update_fields=["current_index"])
        elif action == "prev" and participant.current_index > 0:
            participant.current_index -= 1
            participant.save(update_fields=["current_index"])
        elif action == "finish" and participant.current_index == total_images - 1:
            return redirect("final_survey")

        return redirect("survey_question")

    return render(request, "survey_question.html", {
        "image_path": image_path,
        "index": participant.current_index + 1,
        "total": total_images,
        "can_go_prev": participant.current_index > 0,
        "can_go_next": participant.current_index < total_images - 1,
        "existing_rating": existing_rating.rating if existing_rating else None,
    })

@csrf_exempt
def submit_rating(request):
    if request.method == "POST":
        participant_id = request.session.get("participant_id")
        image_id = request.POST.get("image_id")
        rating = request.POST.get("rating")

        if not participant_id or not image_id or not rating:
            return JsonResponse({"error": "Missing data"}, status=400)

        with transaction.atomic():  # Ensures safe updates
            participant = Participant.objects.select_for_update().get(id=participant_id)
            image = Image.objects.get(id=image_id)

            # Store or update rating
            ImageRating.objects.update_or_create(
                participant=participant,
                image=image,
                defaults={"rating": int(rating)}
            )

            # Move to next image safely
            participant.current_index += 1
            participant.save(update_fields=["current_index"])

        return JsonResponse({"next": participant.current_index})

    return JsonResponse({"error": "Invalid request"}, status=400)

def final_survey(request):
    if request.method == "POST":
        participant_id = request.session.get("participant_id")
        participant = Participant.objects.get(id=participant_id)

        FinalSurvey.objects.create(
            participant=participant,
            contrast=request.POST.get("contrast"),
            sharpness=request.POST.get("sharpness"),
            colorfulness=request.POST.get("colorfulness"),
            brightness=request.POST.get("brightness"),
            comments=request.POST.get("comments", ""),
        )

        del request.session["participant_id"]  # Clear session

        return redirect("thank_you")

    return render(request, "final_survey.html")

def thank_you(request):
    return render(request, "thank_you.html")
