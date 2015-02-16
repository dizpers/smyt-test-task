# coding=utf-8

from functools import partial

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse

from django.db import models
from django.db.models import get_models

from django.test import TestCase, Client
from django.utils.dateparse import parse_date

from django_dynamic_fixture import G, N

from smyt.core import models as core_models
from smyt.core.models import field_mapping_dct


class ModelCreationTestCase(TestCase):

    def test_get_spec_dct(self):
        spec_dct = core_models.get_spec_dct()
        self.assertEqual(spec_dct.keys(), ['users', 'rooms'])
        users_spec_dct = spec_dct['users']
        self.assertEqual(users_spec_dct['title'], u'Пользователи')
        self.assertIn('fields', users_spec_dct)
        self.assertEqual(
            users_spec_dct['fields'],
            [
                {
                    'max_length': 10,
                    'type': 'char',
                    'id': 'name',
                    'title': u'Имя'
                },
                {
                    'type': 'int',
                    'id': 'paycheck',
                    'title': u'Зарплата'
                },
                {
                    'type': 'date',
                    'id': 'date_joined',
                    'title': u'Дата поступления на работу'
                }
            ]
        )
        rooms_spec_dct = spec_dct['rooms']
        self.assertEqual(rooms_spec_dct['title'], u'Комнаты')
        self.assertIn('fields', rooms_spec_dct)
        self.assertEqual(
            rooms_spec_dct['fields'],
            [
                {
                    'max_length': 15,
                    'type': 'char',
                    'id': 'department',
                    'title': u'Отдел'
                },
                {
                    'type': 'int',
                    'id': 'spots',
                    'title': u'Вместимость'
                }
            ]
        )

    def test_models_created_properly(self):
        spec_dct = core_models.get_spec_dct()
        model_cls_lst = get_models(core_models)

        model_cls_name_lst = map(
            lambda model: model.__name__,
            model_cls_lst
        )
        spec_model_cls_name_lst = map(
            lambda name: name.capitalize(),
            spec_dct.keys()
        )
        self.assertEqual(
            model_cls_name_lst,
            spec_model_cls_name_lst
        )

        model_cls_verbose_name_lst = map(
            lambda model: model._meta.verbose_name,
            model_cls_lst
        )
        spec_model_cls_verbose_name_lst = map(
            lambda item: item['title'],
            spec_dct.values()
        )
        self.assertEqual(
            model_cls_verbose_name_lst,
            spec_model_cls_verbose_name_lst
        )

        for model in model_cls_lst:
            spec_model_name = model.__name__.lower()
            spec_model_field_lst = spec_dct[spec_model_name]['fields']

            model_field_name_lst = model._meta.get_all_field_names()
            model_field_name_lst.remove('id')
            spec_model_field_name_lst = sorted(
                map(
                    lambda field: field['id'],
                    spec_model_field_lst
                )
            )
            self.assertEqual(
                model_field_name_lst,
                spec_model_field_name_lst
            )

            model_field_lst = model._meta.local_fields
            model_field_lst = filter(lambda f: not isinstance(f, models.AutoField), model_field_lst)
            for field, spec_field in zip(model_field_lst, spec_model_field_lst):
                self.assertEqual(
                    field.name,
                    spec_field['id']
                )
                self.assertIsInstance(
                    field,
                    field_mapping_dct[spec_field['type']]['class']
                )
                spec_field_title = spec_field.get('title')
                if spec_field_title:
                    self.assertEqual(
                        field.verbose_name,
                        spec_field_title
                    )
                spec_field_max_length = spec_field.get('max_length')
                if spec_field_max_length:
                    self.assertEqual(
                        field.max_length,
                        spec_field_max_length
                    )


class BackboneBackendTestCase(TestCase):

    OBJECTS_MODEL = core_models.Users
    OBJECTS_COUNT = 5

    def setUp(self):
        self.obj_lst = [
            G(self.OBJECTS_MODEL) for _ in xrange(self.OBJECTS_COUNT)
        ]

    def _decode_datetime(self, attrs, obj):
        assert type(attrs) == list
        for attr in attrs:
            try:
                obj[attr] = parse_date(obj[attr])
            except TypeError:
                pass
        return obj

    def test_model_info_good_model(self):
        client = Client()
        response = client.get(reverse('model_info', kwargs={'model': 'Users'}))
        self.assertEqual(response.get('Content-Type'), 'application/json')
        response = json.loads(response.content)
        field_lst = core_models.Users._meta.local_fields
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
        self.assertEqual(
            response,
            field_lst
        )

    def test_model_info_bad_model(self):
        client = Client()
        response = client.get(reverse('model_info', kwargs={'model': 'Ujlskdjf'}))
        self.assertEqual(response.get('Content-Type'), 'application/json')
        response = json.loads(response.content)
        field_lst = []
        self.assertEqual(
            response,
            field_lst
        )

    def test_model_objects_get_good_model(self):
        client = Client()
        response = client.get(
            reverse(
                'model_objects_get',
                kwargs={'model': self.OBJECTS_MODEL.__name__}
            )
        )
        self.assertEqual(response.get('Content-Type'), 'application/json')
        date_field_lst = map(
            lambda field_cls: field_cls.name,
            filter(
                lambda field: isinstance(field, models.DateField),
                self.OBJECTS_MODEL._meta.local_fields
            )
        )
        response = json.loads(
            response.content,
            object_hook=partial(self._decode_datetime, date_field_lst)
        )
        self.assertEqual(len(response), self.OBJECTS_COUNT)
        field_name_lst = self.OBJECTS_MODEL._meta.get_all_field_names()
        self.assertEqual(
            response,
            map(
                lambda obj: {
                    field_name: getattr(obj, field_name) for field_name in field_name_lst
                },
                self.obj_lst
            )
        )

    def test_model_objects_get_bad_model(self):
        client = Client()
        response = client.get(
            reverse(
                'model_objects_get',
                kwargs={'model': self.OBJECTS_MODEL.__name__+'asdfasdf'}
            )
        )
        self.assertEqual(response.get('Content-Type'), 'application/json')
        response = json.loads(response.content)
        self.assertEqual(response, [])

    def test_model_objects_get_create_good_model(self):
        client = Client()
        model_field_lst = self.OBJECTS_MODEL._meta.get_all_field_names()
        model_field_lst.remove('id')
        model_fixture = N(self.OBJECTS_MODEL)
        post_data_dct = {
            field_name: getattr(model_fixture, field_name) for field_name in model_field_lst
        }
        response = client.post(
            reverse(
                'model_objects_get',
                kwargs={'model': self.OBJECTS_MODEL.__name__}
            ),
            json.dumps(post_data_dct, cls=DjangoJSONEncoder),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'

        )
        self.assertEqual(self.OBJECTS_MODEL.objects.count(), len(self.obj_lst)+1)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        date_field_lst = map(
            lambda field_cls: field_cls.name,
            filter(
                lambda field: isinstance(field, models.DateField),
                self.OBJECTS_MODEL._meta.local_fields
            )
        )
        response = json.loads(
            response.content,
            object_hook=partial(self._decode_datetime, date_field_lst)
        )
        self.assertIn('id', response)
        del response['id']
        self.assertEqual(response, post_data_dct)

    def test_model_objects_get_create_bad_model(self):
        client = Client()
        model_field_lst = self.OBJECTS_MODEL._meta.get_all_field_names()
        model_field_lst.remove('id')
        model_fixture = N(self.OBJECTS_MODEL)
        post_data_dct = {
            field_name: getattr(model_fixture, field_name) for field_name in model_field_lst
        }
        response = client.post(
            reverse(
                'model_objects_get',
                kwargs={'model': self.OBJECTS_MODEL.__name__+'asdf'}
            ),
            json.dumps(post_data_dct, cls=DjangoJSONEncoder),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.content, '')
        self.assertEqual(self.OBJECTS_MODEL.objects.count(), len(self.obj_lst))
        other_model_lst = filter(
            lambda cls: not cls == self.OBJECTS_MODEL,
            get_models(core_models)
        )
        for model_cls in other_model_lst:
            self.assertEqual(model_cls.objects.count(), 0)

    def test_model_objects_post_update_good_model(self):
        client = Client()
        model_field_lst = self.OBJECTS_MODEL._meta.get_all_field_names()
        model_fixture = N(self.OBJECTS_MODEL)
        post_data_dct = {
            field_name: getattr(model_fixture, field_name) for field_name in model_field_lst
        }
        random_model_obj = self.OBJECTS_MODEL.objects.order_by('?')[0]
        post_data_dct.update({
            'id': random_model_obj.id
        })
        response = client.post(
            reverse(
                'model_objects_post',
                kwargs={
                    'model': self.OBJECTS_MODEL.__name__,
                    'object_id': random_model_obj.id
                }
            ),
            json.dumps(post_data_dct, cls=DjangoJSONEncoder),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'

        )
        self.assertEqual(self.OBJECTS_MODEL.objects.count(), len(self.obj_lst))
        other_model_lst = filter(
            lambda cls: not cls == self.OBJECTS_MODEL,
            get_models(core_models)
        )
        for model_cls in other_model_lst:
            self.assertEqual(model_cls.objects.count(), 0)
        self.assertEqual(response.content, '')
        random_model_obj_updated = self.OBJECTS_MODEL.objects.get(id=random_model_obj.id)
        for field_name in post_data_dct:
            self.assertEqual(
                getattr(random_model_obj_updated, field_name),
                post_data_dct[field_name]
            )

    def test_model_objects_post_update_bad_model(self):
        client = Client()
        model_field_lst = self.OBJECTS_MODEL._meta.get_all_field_names()
        model_fixture = N(self.OBJECTS_MODEL)
        post_data_dct = {
            field_name: getattr(model_fixture, field_name) for field_name in model_field_lst
        }
        random_model_obj = self.OBJECTS_MODEL.objects.order_by('?')[0]
        post_data_dct.update({
            'id': random_model_obj.id
        })
        response = client.post(
            reverse(
                'model_objects_post',
                kwargs={
                    'model': self.OBJECTS_MODEL.__name__+'sadfas',
                    'object_id': random_model_obj.id
                }
            ),
            json.dumps(post_data_dct, cls=DjangoJSONEncoder),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'

        )
        self.assertEqual(self.OBJECTS_MODEL.objects.count(), len(self.obj_lst))
        other_model_lst = filter(
            lambda cls: not cls == self.OBJECTS_MODEL,
            get_models(core_models)
        )
        for model_cls in other_model_lst:
            self.assertEqual(model_cls.objects.count(), 0)
        response = json.loads(response.content)
        self.assertEqual(response, {})
