import csv
from django.http import HttpResponse
from .models import Image, ImageRating
from .models import FinalSurvey

def export_image_ratings(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="image_ratings.csv"'

    writer = csv.writer(response)
    writer.writerow(["Nama Gambar", "C1", "C2", "C3", "C4", "C5", "MOS"])

    images = Image.objects.all()
    
    for image in images:
        ratings = ImageRating.objects.filter(image=image)
        c1 = ratings.filter(rating=1).count()
        c2 = ratings.filter(rating=2).count()
        c3 = ratings.filter(rating=3).count()
        c4 = ratings.filter(rating=4).count()
        c5 = ratings.filter(rating=5).count()

        total_votes = c1 + c2 + c3 + c4 + c5
        mos = (c1*1 + c2*2 + c3*3 + c4*4 + c5*5) / total_votes if total_votes > 0 else 0

        writer.writerow([image.file_name, c1, c2, c3, c4, c5, round(mos, 2)])

    return response

def export_metric_quantitative_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="metric_quantitative_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Metric", "Rank 1 (Votes)", "Rank 2 (Votes)", "Rank 3 (Votes)", "Rank 4 (Votes)", "Borda Score"])

    metrics = ["contrast", "sharpness", "colorfulness", "brightness"]
    rank_counts = {metric: [0, 0, 0, 0] for metric in metrics}  # Stores count for each rank position

    # Process all surveys
    surveys = FinalSurvey.objects.all()
    for survey in surveys:
        rank_counts["contrast"][survey.contrast - 1] += 1
        rank_counts["sharpness"][survey.sharpness - 1] += 1
        rank_counts["colorfulness"][survey.colorfulness - 1] += 1
        rank_counts["brightness"][survey.brightness - 1] += 1

    # Compute Borda Score and write data to CSV
    for metric, ranks in rank_counts.items():
        borda_score = (ranks[0] * 4) + (ranks[1] * 3) + (ranks[2] * 2) + (ranks[3] * 1)
        writer.writerow([metric, ranks[0], ranks[1], ranks[2], ranks[3], borda_score])

    return response


def export_metric_ranking(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="metric_ranking.csv"'

    writer = csv.writer(response)
    writer.writerow(["Metric", "Score"])

    metrics = ["contrast", "sharpness", "colorfulness", "brightness"]
    scores = {metric: 0 for metric in metrics}

    surveys = FinalSurvey.objects.all()

    for survey in surveys:
        scores["contrast"] += (5 - survey.contrast)  # Higher rank gets higher points
        scores["sharpness"] += (5 - survey.sharpness)
        scores["colorfulness"] += (5 - survey.colorfulness)
        scores["brightness"] += (5 - survey.brightness)

    # Sort metrics based on score
    sorted_metrics = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for metric, score in sorted_metrics:
        writer.writerow([metric, score])

    return response

def export_comments(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comments.csv"'

    writer = csv.writer(response)
    writer.writerow(["Nama Peserta", "Komentar"])

    surveys = FinalSurvey.objects.exclude(comments="")  
    for survey in surveys:
        writer.writerow([survey.participant.name, survey.comments])

    return response
