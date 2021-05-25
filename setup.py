import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# see: https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-py for a description
# see: https://github.com/pypa/sampleproject/blob/master/setup.py for an example
# see: https://pip.pypa.io/en/stable/reference/pip_install for a description how to use pip install in conjunction with a git repository

setuptools.setup(
    name="brainprint",
    version="0.1",
    author="Kersten Diers, Martin Reuter",
    author_email="kersten.diers@dzne.de",
    description="A light-weight package derived from the BrainPrint scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Deep-MI/BrainPrint-python",
    #package_dir={'': 'src'},
    packages=setuptools.find_packages(),
    # see https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT"
#        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    keywords='BrainPrint',
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['numpy', 'scipy']
)
