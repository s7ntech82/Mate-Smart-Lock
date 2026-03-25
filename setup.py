from setuptools import setup, find_packages

setup(
    name='mate-smart-lock',
    version='0.1.0',
    description='Automagic screen lock/unlock based on Bluetooth proximity',
    author='Ismail Nasry',
    author_email='info@ismailnasry.it',
    url='https://ismailnasry.it',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'PyGObject>=3.38.0',
    ],
    entry_points={
        'console_scripts': [
            'mate-smart-lock=mate_smart_lock.main:main',
        ],
    },
    package_data={
        'mate_smart_lock': ['data/*'],
    },
)
