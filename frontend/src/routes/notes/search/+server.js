import { MARKOPOLIS_API_KEY } from '$env/static/private';

async function fetchApiResponse(query, customFetch = fetch) {
    const finalUrl = `http://localhost:8000/api/search/${query}`;
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

export async function GET({ url }) {
  const query = url.searchParams.get('query');
  console.log("quer", query);
  const results = await fetchApiResponse(query);
  console.log("search results: ", results)
  return new Response(JSON.stringify(results), { status: 200 });
}
