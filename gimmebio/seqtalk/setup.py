import setuptools

setuptools.setup(
    name="SeqTalk",
    version="0.9.0",
    url="https://github.com/dcdanko/SeqTalk",

    author="David C. Danko",
    author_email="dcdanko@gmail.com",

    description="",

    packages=['datasuper'],
    package_dir={'datasuper': 'datasuper'},

    install_requires=[],

    entry_points={
        'console_scripts': [
            'datasuper=datasuper.cli:main'
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
