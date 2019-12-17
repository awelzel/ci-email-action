FROM python:3-alpine
COPY process.py /process.py
ENTRYPOINT ["/process.py"]
