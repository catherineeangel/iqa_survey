from django.urls import path
from .views import start_survey, submit_rating, survey_question, final_survey, thank_you
from .utils import export_image_ratings, export_metric_ranking, export_comments, export_metric_quantitative_data

urlpatterns = [
    path("", start_survey, name="start_survey"),
    path("survey/submit/", submit_rating, name="submit_rating"),
    path("survey/", survey_question, name="survey_question"),
    path("final/", final_survey, name="final_survey"),
    path("thank-you/", thank_you, name="thank_you"),

    path("export/image_ratings/", export_image_ratings, name="export_image_ratings"),
    path("export/metric_ranking/", export_metric_ranking, name="export_metric_ranking"),
    path("export/comments/", export_comments, name="export_comments"),
    path("export/metric_quantitative/", export_metric_quantitative_data, name="export_metric_quantitative"),

]