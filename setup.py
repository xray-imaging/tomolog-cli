from setuptools import setup, find_packages

setup(
    name='tomolog-cli',
    version=open('VERSION').read().strip(),
    # version=__version__,
    author='Viktor Nikitin',
    author_email='vnikitin@anl.gov',
    url='https://github.com/nikitivv/tomolog-cli',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/tomologcli.py'],
    entry_points={'console_scripts': ['tomolog = tomologcli:main'], },
    description='cli for loggin data to google slides',
    zip_safe=False,
)
