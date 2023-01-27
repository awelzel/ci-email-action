FROM python:3-alpine
RUN pip3 install requests flake8

COPY setup.cfg process.py test_process.py ./
COPY ./test_data ./test_data

RUN flake8 ./process.py ./test_process.py
RUN python3 -m unittest -v ./test_process.py
