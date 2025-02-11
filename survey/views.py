import os
import random
from django.shortcuts import render, redirect
from .models import Participant, Image, ImageRating, FinalSurvey
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def start_survey(request):
    if request.method == "POST":
        name = request.POST.get("name")
        participant = Participant.objects.create(name=name)

        # Get all stored images from the database
        stored_images = list(Image.objects.all())

        # Pick 30 random images
        selected_images = random.sample(stored_images, min(30, len(stored_images)))

        # Store selected image IDs in session
        request.session["participant_id"] = participant.id
        request.session["image_ids"] = [img.id for img in selected_images]
        request.session["index"] = 0  # Start index

        return redirect("survey_question")

    return render(request, "start_survey.html")


def survey_question(request):
    participant_id = request.session.get("participant_id")
    image_ids = request.session.get("image_ids", [])
    index = request.session.get("index", 0)

    if not participant_id:
        return redirect("final_survey")

    participant = Participant.objects.get(id=participant_id)
    total_images = len(image_ids)

    # Ensure index does not go out of bounds
    if index >= total_images:
        return redirect("final_survey")

    # Get current image
    image = Image.objects.get(id=image_ids[index])

    # Check if this image has already been rated by this participant
    existing_rating = ImageRating.objects.filter(participant=participant, image=image).first()

    if request.method == "POST":
        action = request.POST.get("action")
        rating_value = request.POST.get("rating")

        # Ensure a rating is selected before navigating
        if action in ["next", "finish"] and not rating_value:
            return render(request, "survey_question.html", {
                "image": image,
                "image_path": f"/static/images/{image.file_name}",
                "index": index + 1,
                "total": total_images,
                "can_go_prev": index > 0,
                "can_go_next": index < total_images - 1,
                "existing_rating": existing_rating.rating if existing_rating else None,
                "error": "Please select a rating before proceeding."
            })

        # Save or update rating
        if rating_value:
            if existing_rating:
                existing_rating.rating = int(rating_value)
                existing_rating.save()
            else:
                ImageRating.objects.create(participant=participant, image=image, rating=int(rating_value))

        # Navigation Logic
        if action == "next" and index < total_images - 1:
            request.session["index"] += 1
        elif action == "prev" and index > 0:
            request.session["index"] -= 1
        elif action == "finish" and index == total_images - 1:  # ✅ Fix condition
            return redirect("final_survey")

        return redirect("survey_question")

    return render(request, "survey_question.html", {
        "image": image,
        "image_path": f"/static/images/{image.file_name}",
        "index": index + 1,  # Display 1-based index for user
        "total": total_images,
        "can_go_prev": index > 0,
        "can_go_next": index < total_images - 1,
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

        participant = Participant.objects.get(id=participant_id)
        image = Image.objects.get(id=image_id)

        # Store rating in database
        ImageRating.objects.create(participant=participant, image=image, rating=int(rating))

        # Move to the next image
        request.session["index"] += 1

        return JsonResponse({"next": request.session["index"]})

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
        del request.session["image_ids"]
        del request.session["index"]

        return redirect("thank_you")

    return render(request, "final_survey.html")

def thank_you(request):
    return render(request, "thank_you.html")
