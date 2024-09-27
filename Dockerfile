FROM alpine:latest

ARG PB_VERSION=0.22.21
ARG POCKETBASE_ADMIN_EMAIL=admin@example.com
ARG POCKETBASE_ADMIN_PASSWORD=admin123

RUN apk add --no-cache \
    unzip \
    ca-certificates \
    curl

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

# create PocketBase data directory
RUN mkdir -p /pb/pb_data
COPY start.sh /pb/start.sh

# start PocketBase in a background process to set up the database
RUN chmod +x /pb/start.sh

# uncomment to copy the local pb_migrations dir into the image
# COPY ./pb_migrations /pb/pb_migrations

# uncomment to copy the local pb_hooks dir into the image
# COPY ./pb_hooks /pb/pb_hooks

EXPOSE 8080

# start PocketBase
CMD ["/pb/start.sh"]
