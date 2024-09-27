import PocketBase from 'pocketbase';
import {
	POCKETBASE_URL,
	POCKETBASE_ADMIN_EMAIL,
	POCKETBASE_ADMIN_PASSWORD
} from '$env/static/private';

let pocketBaseInstance: PocketBase | null = null;

export async function getAuthenticatedPocketBase() {
	if (!pocketBaseInstance) {
		pocketBaseInstance = new PocketBase(POCKETBASE_URL);
		pocketBaseInstance.autoCancellation(false); // Prevent cancellation of overlapping requests
	}

	// Check if the current authentication is valid
	if (pocketBaseInstance.authStore.isValid) {
		try {
			console.log('login valid');

			// Check if logged in as a user (not admin) and refresh token
			if (pocketBaseInstance.authStore.model?.email !== POCKETBASE_ADMIN_EMAIL) {
				// Only refresh tokens for non-admin users
				await pocketBaseInstance.collection('users').authRefresh();
				console.log('Token refreshed successfully');
			}

			return pocketBaseInstance;
		} catch (error) {
			console.error('Token refresh failed:', error);
		}
	}

	// Login as admin if token is invalid or refresh failed
	try {
		console.log('Attempting to log in as admin...');
		await pocketBaseInstance.admins.authWithPassword(
			POCKETBASE_ADMIN_EMAIL,
			POCKETBASE_ADMIN_PASSWORD
		);
		console.log('New admin authentication successful');
		return pocketBaseInstance;
	} catch (error) {
		// Log any error encountered during login
		console.error('Admin login failed:', error);
		throw error;
	}
}
