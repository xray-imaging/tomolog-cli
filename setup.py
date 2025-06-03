from setuptools import setup, find_packages

setup(
    name='tomolog-cli',
    version=open('VERSION').read().strip(),
    author='Viktor Nikitin',
    author_email='vnikitin@anl.gov',
    url='https://github.com/xray-imaging/tomolog-cli',

    package_dir={"": "src"},
    entry_points={'console_scripts':['tomolog = tomolog_cli.__main__:main'],},
    packages=find_packages('src'),
    description='cli for loggin data to google slides',
    zip_safe=False,
)
