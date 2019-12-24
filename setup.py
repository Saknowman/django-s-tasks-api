import os

import setuptools

readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_file, 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="django-s-tasks-api",
    version="1.0.0",
    author="Yuki Sakumoto",
    author_email="snowman.sucking@gmail.com",
    description="django-s-tasks-api is a simple tasks rest api of django.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Saknowman/django-s-tasks-api",
    packages=[
        's_tasks_api', 's_tasks_api.fixtures', 's_tasks_api.migrations',
        's_tasks_api.permissions', 's_tasks_api.services',
        's_tasks_api.tests', 's_tasks_api.tests.tasks',

    ],
    license="MIT",
    install_requires=["Django>=3.0", "djangorestframework>=3.10", "django-filter==2.2.0"],
    classifiers=[
        'Framework :: Django :: 3.0',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
