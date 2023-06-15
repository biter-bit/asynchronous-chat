from cx_Freeze import setup, Executable

executables = [
    Executable('client.py', base='Win32GUI', target_name='client.exe')
]
build_exe_options = {
    'packages': [],
}

setup(
    name='chat_async_client_exe',
    version='1.0.0',
    description='description',
    author='Michael Kurashev',
    author_email='kurashevmichael@gmail.com',
    options={
        'build_exe': build_exe_options
    },
    executables=executables,
)