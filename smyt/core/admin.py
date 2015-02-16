from django.contrib import admin

from django.db.models import get_models

from smyt.core import models

model_lst = get_models(models)
for model in model_lst:
    admin.site.register(model)
