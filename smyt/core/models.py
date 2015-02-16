import sys
import json

import yaml

from django.conf import settings
from django.db import models


field_mapping_dct = {
    'char': {
        'class': models.CharField,
        'kwargs': {
            'name_mapping': {
                'title': 'verbose_name'
            },
            'defaults': {
                'max_length': 255
            }
        }
    },
    'int': {
        'class': models.IntegerField,
        'kwargs': {
            'name_mapping': {
                'title': 'verbose_name'
            }
        }
    },
    'date': {
        'class': models.DateField,
        'kwargs': {
            'name_mapping': {
                'title': 'verbose_name'
            }
        }
    }
}

spec_processing_mapping_dct = {
    'yaml': yaml.load,
    'json': json.loads
}


def get_spec_dct():
    model_spec_file_extension = settings.MODEL_SPEC_FILE.split('.')[-1]
    with open(settings.MODEL_SPEC_FILE, 'r') as f:
        return spec_processing_mapping_dct[model_spec_file_extension](
            f.read()
        )

spec_dct = get_spec_dct()
for model_name in spec_dct:
    # get model spec
    model_spec = spec_dct[model_name]

    # create model Meta class
    model_meta_kwargs = {}
    model_title = model_spec.get('title')
    if model_title:
        model_meta_kwargs.update({
            'verbose_name': model_title
        })
    model_meta_cls = type('Meta', (), model_meta_kwargs)

    # create actual model here
    model_kwargs = {
        '__module__': __name__,
        'Meta': model_meta_cls
    }
    model_fields = model_spec.get('fields', [])
    for field in model_fields:
        field_kwargs = {}
        field_type = field.pop('type')
        field_name = field.pop('id')
        field_class = field_mapping_dct[field_type]['class']
        # name field kwargs according to mapping
        for old_field_name, new_field_name in field_mapping_dct[field_type]['kwargs']['name_mapping'].items():
            field[new_field_name] = field.pop(old_field_name)
        # apply default kwargs first
        field_kwargs.update(field_mapping_dct[field_type]['kwargs'].get('defaults', {}))
        # when apply the rest
        field_kwargs.update(field)
        # create field and add it to model class
        model_kwargs.update({
            field_name: field_class(**field_kwargs)
        })
    model_cls = type(model_name.capitalize(), (models.Model,), model_kwargs)
    setattr(sys.modules[__name__], model_cls.__name__, model_cls)