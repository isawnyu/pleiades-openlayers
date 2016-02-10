from setuptools import setup, find_packages

version = '0.3'

setup(name='pleiades.openlayers',
      version=version,
      description="OpenLayers support for Pleiades",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Sean Gillies',
      author_email='sean.gillies@gmail.com',
      url="''",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pleiades'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.geo.geographer',
          'geojson',
          'pyproj',
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
