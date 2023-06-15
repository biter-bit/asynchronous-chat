#!/bin/bash

export PYTHONPATH=/home/michael/python_work/asynchronous_chat_gb/
gnome-terminal -- bash -c 'python server_back/server_back.py; exec bash'
sleep 1
gnome-terminal -- bash -c 'python client_front/client_front.py; exec bash'