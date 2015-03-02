from setuptools import setup

long_description = (open('README.rst').read() + '\n\n' +
                    open('CHANGES.rst').read() + '\n\n' +
                    open('TODO.rst').read())

def _static_files(prefix):
    return [prefix+'/'+pattern for pattern in [
        'joyride/*.*',
        'joyride/*/*.*',
    ]]

setup(
    name='django-joyride',
    version='0.1.2',
    description='A Django application that eases the guided tour',
    author='Aamir Adnan',
    author_email='s33k.n.d3str0y@gmail.com',
    url='https://github.com/intellisense/django-joyride',
    license='MIT',
    packages=['joyride', 'joyride.templatetags'],
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-positions>=0.5.0',
        'Django>=1.4.3'
    ],
    package_data={'joyride': ['templates/joyride/*.html'] +
                              _static_files('static')}
)
