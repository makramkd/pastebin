FROM python:3.6-stretch as python-dev
WORKDIR /src/pastebin

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY setup.py ./

COPY pastebin ./pastebin
RUN python setup.py install

EXPOSE 8000

CMD ["pastebin"]
