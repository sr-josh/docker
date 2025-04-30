# base image
FROM python:3.9.1

# installing prerequisites
RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

# working directory inside cont
WORKDIR /app

# copy the script to the cont
COPY /jupyter/ingest_data.py ingest_data.py

# what to do first
ENTRYPOINT ["python", "ingest_data.py"]
