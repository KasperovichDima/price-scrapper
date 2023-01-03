FROM python:3.10
WORKDIR /app
COPY . .
RUN apt-get update -y \
&& apt-get install -y mc
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
WORKDIR /app/src
# CMD uvicorn main:app --host 0.0.0.0 --port 8000



# delete all unnecessary from requirements.txt