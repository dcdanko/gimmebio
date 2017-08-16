import setuptools

setuptools.setup(
    name="gimmebio",
    version="0.1.0",
    url="https://github.com/dcdanko/gimmebio.git",

    author="David C. Danko",
    author_email="dcdanko@gmail.com",

    description="Common functions for comp. bio",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    ext_modules = [setuptools.Extension("ckmers", ["cext_gimmebio/_ckmers.c","cext_gimmebio/ckmers.c"])],
    
    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
