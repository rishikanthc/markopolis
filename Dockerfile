FROM python:3.12-alpine

RUN pip install --no-cache-dir markopolis==0.2.0

WORKDIR /app

EXPOSE 8080

# Run Python interactive shell when the container launches
CMD ["markopolis", "run", "--port", "8080"]
