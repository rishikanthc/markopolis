
export default async function fetchApiResponse(apiEndpoint, customFetch = fetch) {
    const baseUrl = 'http://localhost:8000';
    const finalUrl = baseUrl + apiEndpoint;
    try {
        const response = await customFetch(finalUrl, {
            method: 'GET',
            headers: {
                'x-api-key': 'test',
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
