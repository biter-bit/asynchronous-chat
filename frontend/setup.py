from setuptools import setup, find_packages

setup(
    name='async_chat_front',
    version='1.0.1',
    description='mess_server_proj',
    author='Michael Kurashev',
    author_email='kurashevmichael@gmail.com',
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
)
