import os

from glob import glob
from setuptools import find_packages, setup



docker_data_files = []
for filepath in glob('notsocode/dockerfiles/**', recursive=True):
    if not os.path.isdir(filepath):
        docker_data_files.append(filepath)

install_requires = [
    'docker==7.1.0',
    'types-requests==2.32.0.20241016',
    'python-dotenv==0.21.1',
]

server_requires = [
    'sanic==24.6.0',
    'sanic_dantic @ git+https://github.com/notsobot/nsb.api.sanic-dantic.git@all-parameter',
    'pydantic==2.10.2',
    'python-dotenv==1.0.1',
]

setup_kwargs = {
    'name': 'notsocode',
    'version': '2.0.0',
    'url': 'https://github.com/notsobot/notsocode',
    'author': 'cake',
    'description': (
        'Safely execute remote code in docker while being able to pass/read files between them',
    ),
    'packages': find_packages(),
    'package_data': {
        'notsocode': ['py.typed'],
        'notsocode_server': ['py.typed'],
    },
    'include_package_data': True,
    'platforms': 'any',
    'install_requires': install_requires,
    'extras_require': {
        'server': server_requires,
    },
    'entry_points': {
        'console_scripts': ['notsocodeserver = notsocode_server.__main__:start'],
    },
    'data_files': [
        ('notsocode/dockerfiles', docker_data_files),
    ],
}

setup(**setup_kwargs)
