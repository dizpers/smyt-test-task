from .local import *

INSTALLED_APPS += (
    'django_nose',
)

NOSE_ARGS = [
    '--failed',
    '--stop',
    '--verbosity=3'
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MODEL_SPEC_FILE = os.path.join(MODEL_SPEC_DIR, 'test_spec.yaml')