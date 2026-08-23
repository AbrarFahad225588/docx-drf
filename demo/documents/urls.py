from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path(
        "api/generate-form/",
        views.GenerateApplicationFormView.as_view(),
        name="generate-form",
    ),
    path(
        "api/download-template/",
        views.DownloadBlankTemplateView.as_view(),
        name="download-template",
    ),
    path(
        "api/generate-form-pdf/",
        views.GenerateFormPDFView.as_view(),
        name="generate-form-pdf",
    ),
    path(
        "api/template-fields/",
        views.TemplateFieldsView.as_view(),
        name="template-fields",
    ),
]
