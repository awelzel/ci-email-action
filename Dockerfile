FROM python:3-alpine
COPY process.py /process.py
RUN pip3 install requests
ENTRYPOINT ["/process.py"]
