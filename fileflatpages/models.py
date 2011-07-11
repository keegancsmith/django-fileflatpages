from django.contrib.flatpages.models import FlatPage
from django.db import models

class FileFlatPage(FlatPage):
    app = models.TextField()
    path = models.TextField()
