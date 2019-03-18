from setuptools import setup

microlib_name = 'gimmebio.hiveplots'

requirements = [
    'matplotlib',
    'pandas',
]

setup(
    name=microlib_name,
    version='0.5.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    namespace_packages=['gimmebio'],
    packages=[microlib_name, f'{microlib_name}.colors'],
    install_requires=requirements,
)
