#!/bin/bash

list_name_file=(server)
mkdir -p /home/michael/python_work/asynchronous_chat_gb/backend/pep/

for i in ${list_name_file[@]}
do
  echo -e "---------------------------------------------\nПроверка файла $i.py\n"
  echo -n > "/home/michael/python_work/asynchronous_chat_gb/backend/pep/result_$i.txt"
  PATH_FILE=`find /home/michael/python_work/asynchronous_chat_gb/backend/ -name $i.py`
  flake8 "$PATH_FILE" | tee "/home/michael/python_work/asynchronous_chat_gb/backend/pep/result_$i.txt"
  VAR1=`cat "/home/michael/python_work/asynchronous_chat_gb/backend/pep/result_$i.txt"`
  if [[ -z $VAR1 ]]
  then
    echo "The verification of the $i.py file is completed. No errors detected"
  fi
done