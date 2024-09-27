# Use Node.js alpine as the base image
FROM node:18-alpine

ARG PB_VERSION=0.22.21

RUN apk add --no-cache \
    unzip \
    ca-certificates

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

# Uncomment to copy the local pb_migrations dir into the image
# COPY ./pb_migrations /pb/pb_migrations

# Uncomment to copy the local pb_hooks dir into the image
# COPY ./pb_hooks /pb/pb_hooks

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install SvelteKit dependencies
RUN npm install

# Copy the rest of the SvelteKit app's source code
COPY . .

# Expose the PocketBase HTTP port
EXPOSE 8090 3000

# Copy the start.sh script into the container
COPY start.sh /start.sh

# Make the script executable
RUN chmod +x /start.sh

# Use the script to start PocketBase and create the admin user
RUN ["/bin/sh", "/start.sh"]

# Install supervisor
RUN apk add --no-cache supervisor

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

# CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8090", "--dev", "&&", "echo", "hello"]
# CMD echo "hello" & \
#     /pb/pocketbase serve --http=0.0.0.0:8090 --dev & \
#     /usr/local/bin/node build &
