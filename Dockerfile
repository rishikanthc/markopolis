FROM python:3.12-alpine

# Install ripgrep
RUN apk add --no-cache ripgrep

# Install markopolis
RUN pip install --no-cache-dir markopolis==1.1.1

WORKDIR /app

EXPOSE 8080

# Run markopolis when the container launches
CMD ["markopolis", "run", "--port", "8080"]
