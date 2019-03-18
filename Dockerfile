FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./truthdiscovery/ /app/truthdiscovery
COPY ./setup.py /app/setup.py
COPY ./README.md /app/README.md
COPY ./requirements.txt /app/requirements.txt

# The base image requires the flask script to be at /app/main.py
RUN cp /app/truthdiscovery/client/web/server.py /app/main.py

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org .

RUN echo "[uwsgi]" > uwsgi.ini
RUN echo "module = truthdiscovery.client.web.server " >> uwsgi.ini
RUN echo "callable=app" >> uwsgi.ini

ENV STATIC_PATH /app/truthdiscovery/client/web/static
