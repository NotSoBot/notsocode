from setuptools import find_packages, setup



install_requires = [
    'docker==6.0.1',
    'types-requests==2.28.11.14',
    'python-dotenv==0.21.1',
]

server_requires = [
    'sanic==22.12.0',
    'sanic_dantic @ git+https://github.com/notsobot/nsb.api.sanic-dantic.git@all-parameter',
    'pydantic==1.10.5',
]

setup_kwargs = {
    'name': 'notsocode',
    'version': '1.0.0',
    'url': 'https://github.com/notsobot/notsocode',
    'author': 'cake',
    'description': (
        'Safely execute remote code in docker while being able to pass/read files between them',
    ),
    'packages': find_packages(where='src'),
    'platforms': 'any',
    'install_requires': install_requires,
    'extras_require': {
        'server': server_requires,
    },
    'entry_points': {
        'console_scripts': ['notsocodeserver = server.app:start'],
    },
}

setup(**setup_kwargs)
