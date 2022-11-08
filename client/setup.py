from distutils.core import setup

setup(name='lwdb',
      version='0.0',
      description='LWDB',
      author='Rick Wierenga',
      author_email='rick_wierenga@icloud.com',
      url='https://www.github.com/pylabrobot/lwdb/',
      packages=['lwdb'],
      requires=['requests'],
      entry_points={
            'console_scripts': [
                  'lwdb = lwdb.__main__:main'
            ]
      }
)
