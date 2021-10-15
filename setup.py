from pip._internal.network.session import PipSession
from setuptools import setup, find_packages

try:
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements

requires = []
links = []

requirements = parse_requirements("requirements.txt", session=PipSession())

for item in requirements:
    if getattr(item, "url", None):
        links.append(str(item.url))
    if getattr(item, "link", None):
        links.append(str(item.link))
    try:
        requires.append(str(item.req))
    except:
        requires.append(str(item.requirement))

f = open("README.md", "r")
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name="wemulate-api",
    version="0.0.1",
    description="API for the modern WAN Emulator (WEmulate)",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Julian Klaiber, Severin Dellsperger",
    author_email="julian.klaiber@ost.ch, severin.dellsperger@ost.ch",
    url="https://github.com/wemulate/wemulate-api",
    license="GPL-3.0",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    entry_points="""
        [console_scripts]
        wemulate-api = api.api:main
    """,
    install_requires=requires,
    dependency_links=links,
)
