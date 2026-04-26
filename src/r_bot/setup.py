from setuptools import setup
import os
from glob import glob

package_name = 'r_bot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@todo.com',
    description='Holonomic robot package',
    license='Apache License 2.0',

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],

    entry_points={
        'console_scripts': [
            'omni_kinematics = r_bot.omni_kinematics:main',
        ],
},
)