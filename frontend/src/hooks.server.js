// src/hooks.server.js
export async function handle({ event, resolve }) {
  const { url } = event;

  // Check if the request is for an image
  const imageExtensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'];
  const isImage = imageExtensions.some(ext => url.pathname.endsWith(ext));

  if (isImage) {
    try {
      // Proxy the request to the backend server
      const backendUrl = `http://localhost:8000${url.pathname}`;
      const response = await fetch(backendUrl);

      if (response.ok) {
        // If the backend returns a successful response, pass it through
        return new Response(response.body, {
          headers: {
            'Content-Type': response.headers.get('Content-Type') || 'image/*'
          }
        });
      } else {
        // Handle errors or return 404 if image not found
        return new Response('Image not found', { status: 404 });
      }
    } catch (error) {
      // Handle network errors
      return new Response('Error fetching image', { status: 500 });
    }
  }

  // For all other requests, pass them to the default resolver
  return resolve(event);
}
