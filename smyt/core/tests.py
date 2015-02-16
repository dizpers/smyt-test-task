# coding=utf-8

from django.test import TestCase
from django.db.models import get_models
from django.db import models
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