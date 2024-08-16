FROM python:3.12-alpine

RUN pip install --no-cache-dir markopolis==0.3.4

WORKDIR /app

EXPOSE 8080

# Run markopolis when the container launches
CMD ["markopolis", "run", "--port", "8080"]
