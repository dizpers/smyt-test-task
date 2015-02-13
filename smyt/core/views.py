import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import TemplateView
from django.db import models
from django.db.models import get_models
from smyt.core import models as core_models


class IndexView(TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx['model_lst'] = get_models(core_models)
        return ctx


def model_info(request, model):
    model_cls = getattr(core_models, model)
    field_lst = model_cls._meta.local_fields
    field_lst = filter(lambda field: not isinstance(field, models.AutoField), field_lst)
    field_lst = map(
        lambda field: {
            'name': field.name,
            'label': getattr(field, 'verbose_name', field.name),
            'cell': 'date' if isinstance(field, models.DateField) else
                    'integer' if isinstance(field, models.IntegerField) else
                    'string',
            'required': not field.empty_strings_allowed,
            'max_length': field.max_length
        },
        field_lst
    )
    return HttpResponse(json.dumps(field_lst), content_type='application/json')


@csrf_exempt
def model_objects(request, model, object_id=None):
    model_cls = getattr(core_models, model)
    if request.method == 'POST':
        obj_data = json.loads(request.body)
        if object_id:
            obj_data.pop('id')
            model_cls.objects.filter(id=object_id).update(**obj_data)
        else:
            model_cls.objects.create(**obj_data)
        return HttpResponse()
    else:
        field_name_lst = model_cls._meta.get_all_field_names()
        obj_lst = model_cls.objects.all()
        obj_lst = map(
            lambda obj: {
                field_name: getattr(obj, field_name) for field_name in field_name_lst
            },
            obj_lst
        )
        return HttpResponse(json.dumps(obj_lst, cls=DjangoJSONEncoder), content_type='application/json')