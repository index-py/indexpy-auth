# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indexpy_auth']

package_data = \
{'': ['*']}

install_requires = \
['index.py>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'indexpy-auth',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Index.py Authentication\n\n## 安装\n\n```\npip install indexpy-auth\n```\n\n## 用例\n',
    'author': 'abersheeran',
    'author_email': 'me@abersheeran.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/index-py/indexpy-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

