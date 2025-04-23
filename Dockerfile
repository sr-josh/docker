# base image
FROM python:3.9.1

# installing prerequisites
RUN pip install pandas

# working directory inside cont
WORKDIR /app

# copy the script to the cont
COPY pipeline.py pipeline.py

# what to do first
ENTRYPOINT ["python", "pipeline.py"]
