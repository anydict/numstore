from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='numstore',
    version='1.2.6',
    author='anydict',
    author_email='novi4kom@gmail.com',
    license='MIT',
    description='numstore - fast and easy key-value storage in RAM. It only works with numbers keys and numbers values',
    long_description=readme(),
    long_description_content_type='text/markdown',
    py_modules=['numstore'],
    scripts=['numstore.py'],
    url='https://github.com/anydict/numstore',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
    ],
    keywords='fast easy key value storage RAM memory only for number',
    python_requires='>=3.10'
)
