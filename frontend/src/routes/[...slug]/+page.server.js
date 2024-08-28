/* import fetchApiResponse from '$lib/util.js'; */
import { MARKOPOLIS_DOMAIN, MARKOPOLIS_FRONTEND_URL, MARKOPOLIS_API_KEY } from '$env/static/private';

async function fetchApiResponse(apiEndpoint, customFetch = fetch) {
    const baseUrl = 'http://localhost:8000';
    const finalUrl = baseUrl + apiEndpoint;
    try {
        const response = await customFetch(finalUrl, {
            method: 'GET',
            headers: {
                'x-api-key': `${MARKOPOLIS_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching API response:', error);
        return null;  // Return null or handle the error as needed
    }
}


// Helper function to prefix relative image URLs
function prefixImageUrls(htmlContent, baseUrl) {
    // Use a regex to find all <img> tags with a src that does not start with http or https
    const regex = /<img\s+[^>]*src=["']([^"']+)["'][^>]*>/g;

    return htmlContent.replace(regex, (match, src) => {
        // Check if the src starts with http or https
        if (!src.startsWith('http://') && !src.startsWith('https://')) {
            // Prefix the src with the base URL
            const newSrc = `${baseUrl}${src.startsWith('/') ? '' : '/'}${src}`;
            // Replace the old src with the new prefixed src
            return match.replace(src, newSrc);
        }
        return match; // No changes for absolute URLs
    });
}

export async function load({ fetch, params }) {
    try {
        const [content, frontmatter, backlinks] = await Promise.all([
            fetchApiResponse(`/api/${params.slug}`, fetch),
            fetchApiResponse(`/api/${params.slug}/frontmatter`, fetch),
            fetchApiResponse(`/api/${params.slug}/backlinks`, fetch),
        ]);

        // Define your base URL
        /* const base_url = 'http://localhost:8000'; */
        const base_url = MARKOPOLIS_DOMAIN + '/api';
        const frontend_url = MARKOPOLIS_FRONTEND_URL;

        // Modify the content.html_content to prefix image URLs
        content.html_content = prefixImageUrls(content.html_content, base_url);

        return {
            content,
            frontmatter,
            backlinks,
            frontend_url
        };
    } catch (err) {
        console.error('Error fetching or parsing data:', err);
        return {
            error: err.message
        };
    }
}
