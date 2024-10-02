#!/bin/sh

# Ensure the environment variables are correctly set
echo "Creating admin with email: ${POCKETBASE_ADMIN_EMAIL}"
echo "PocketBase URL: ${POCKETBASE_URL}"

# Start PocketBase in the background
/pb/pocketbase serve --http=0.0.0.0:8080 --dir /app/db &

# Wait for PocketBase to start (adjust the sleep time if necessary)
sleep 5

# Create the admin user using environment variables
/pb/pocketbase admin create "${POCKETBASE_ADMIN_EMAIL}" "${POCKETBASE_ADMIN_PASSWORD}" --dir /app/db

sleep 2

npm run build

# Build the SvelteKit app (requires PocketBase to be running)
node build

# # Optional: Log environment variables for debugging
# echo "PocketBase URL: ${POCKETBASE_URL}"
# echo "API Key: ${API_KEY}"
# echo "Title: ${TITLE}"
