from setuptools import setup, find_packages

setup(
    name='chat_async_server',
    version='1.0.0',
    description='description',
    author='Michael Kurashev',
    author_email='kurashevmichael@gmail.com',
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines()
)
