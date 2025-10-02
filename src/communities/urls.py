from django.urls import path

from . import views

app_name = "communities"

urlpatterns = [
    # Geographic Data URLs
    path("geographic-data/", views.geographic_data_list, name="geographic_data_list"),
    path("geographic-data/add-layer/", views.add_data_layer, name="add_data_layer"),
    path(
        "geographic-data/create-visualization/",
        views.create_visualization,
        name="create_visualization",
    ),
]
