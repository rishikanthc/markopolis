FROM node:22.9.0-alpine3.20

ARG POCKETBASE_ADMIN_EMAIL
ARG POCKETBASE_ADMIN_PASSWORD
ARG POCKETBASE_URL
ARG TITLE
ARG API_KEY
ARG CAP1
ARG CAP2
ARG CAP3

# Set environment variables to be overridden at runtime
ENV POCKETBASE_ADMIN_EMAIL=$POCKETBASE_ADMIN_EMAIL
ENV POCKETBASE_ADMIN_PASSWORD=$POCKETBASE_ADMIN_PASSWORD
ENV POCKETBASE_URL=$POCKETBASE_URL
ENV TITLE=$TITLE
ENV API_KEY=$API_KEY
ENV CAP1=$CAP1
ENV CAP2=$CAP2
ENV CAP3=$CAP3

# Install required packages
RUN apk update && apk add --no-cache \
    unzip \
    curl

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v0.22.21/pocketbase_0.22.21_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

# create PocketBase data directory
RUN mkdir -p /pb/pb_data
# COPY start.sh /pb/start.sh

# start PocketBase in a background process to set up the database
# RUN chmod +x /pb/start.sh

# uncomment to copy the local pb_migrations dir into the image
# COPY ./pb_migrations /pb/pb_migrations

# uncomment to copy the local pb_hooks dir into the image
# COPY ./pb_hooks /pb/pb_hooks

WORKDIR /app
COPY . .
COPY start_services.sh /app/start.sh

RUN npm ci

# RUN /pb/start.sh

EXPOSE 3000 8080

# start PocketBase
CMD ["/bin/sh", "/app/start.sh"]
