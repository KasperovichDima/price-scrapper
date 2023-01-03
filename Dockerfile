FROM python:3.10
WORKDIR /app
# COPY . .
RUN git clone
RUN apt-get update -y \
&& apt-get install -y mc nano
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
WORKDIR /app/src
CMD uvicorn main:app --host 0.0.0.0 --port 8000



# docker build . -t monitoring:dev