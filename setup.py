import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = unicode(open(os.path.join(here, 'README.md')).read(), 'utf-8')
CHANGES = unicode(open(os.path.join(here, 'CHANGES.rst')).read(), 'utf-8')
REQUIRES = [line.strip() for line in open(os.path.join(here, 'requirements.txt')).readlines()]
SOURCES = []

for index, dependency in enumerate(REQUIRES):
    if dependency.find('#egg=') >= 0:
        SOURCES.append(dependency)
        REQUIRES[index] = dependency[dependency.find('#egg=') + 5:]

setup(name='eventframe',
      version='0.1.0',
      description='Event frame provides functionality common across HasGeek events, to simplify the process of setting up per-event websites.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Intended Audience :: Developers",
          "Development Status :: 3 - Alpha",
          "Topic :: Software Development :: Libraries",
        ],
      author='Kiran Jonnalagadda',
      author_email='kiran@hasgeek.com',
      url='https://github.com/hasgeek/baseframe',
      keywords='baseframe',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      dependency_links=SOURCES,
      )
