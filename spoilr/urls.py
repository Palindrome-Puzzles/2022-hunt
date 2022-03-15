from django.urls import include, path

urlpatterns = [
    path('', include('spoilr.core.urls')),
    path('', include('spoilr.hq.urls')),
    path('', include('spoilr.hq.legacy_urls')),

    # NB: We can't add a prefix to email's automatically yet, as the incoming
    # email view URL shouldn't change.
    path('', include('spoilr.email.urls')),
    path('contact/', include('spoilr.contact.urls')),
    path('events/', include('spoilr.events.urls')),
    path('hints/', include('spoilr.hints.urls')),
    path('interaction/', include('spoilr.interaction.urls')),
    path('progress/', include('spoilr.progress.urls')),
]
