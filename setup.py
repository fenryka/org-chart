from setuptools import setup

setup(
    name='org-chart',
    include_package_data=True,
    version='1.0',
    py_modules=['org_chart'],
    install_requires=[
        'click', 'PyQt5', 'scipy', 'ete3', 'six', 'webcolors'
    ],
    entry_points='''
        [console_scripts]
        orgchart=org_chart:cli
    ''',
)
