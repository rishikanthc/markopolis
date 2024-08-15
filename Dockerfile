FROM python:3.12-alpine

# Install required packages
RUN apk add --no-cache bash

# Install markopolis
RUN pip install --no-cache-dir markopolis==0.3.0

# Set working directory
WORKDIR /app

# Copy the .env file if it exists
COPY .env* /app/

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ -f /app/.env ]; then\n\
    export $(cat /app/.env | xargs)\n\
fi\n\
exec markopolis run --port 8080\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8080

# Run the startup script when the container launches
CMD ["/app/start.sh"]
