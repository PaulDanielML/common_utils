import setuptools

__version__ = "0.1"


def _read_requirements():
    try:
        return open("requirements.txt").read()
    except IOError:
        return ""


install_requires = [l for l in _read_requirements().split("\n") if l and not l.startswith("#")]

setuptools.setup(
    name="helpers",
    version=__version__,
    author="Paul Daniel",
    author_email="paudan22@gmail.com",
    description="Collection of frequently used, repository unspecific Python helpers",
    url="https://github.com/PaulDanielML/common_utils",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
)
