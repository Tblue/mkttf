FROM python:3.7-buster

RUN apt update && apt install -y python-fontforge potrace xfonts-utils

WORKDIR /opt/mkttf
COPY . /opt/mkttf

ENTRYPOINT ["./mktty.py"]
CMD ["-h"]
