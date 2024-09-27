import PocketBase from 'pocketbase';
import {
	POCKETBASE_URL,
	POCKETBASE_ADMIN_EMAIL,
	POCKETBASE_ADMIN_PASSWORD
} from '$env/static/private';

let serverPb: PocketBase | null = null;

export async function getAuthenticatedPocketBase() {
	if (!serverPb) {
		serverPb = new PocketBase(POCKETBASE_URL);
		serverPb.autoCancellation(false);
	}

	// Check if already authenticated and try refreshing the token
	if (serverPb.authStore.isValid) {
		try {
			await serverPb.collection('users').authRefresh();
			console.log('Using existing server authentication');
			return serverPb;
		} catch (error) {
			console.log('Server token refresh failed, re-authenticating');
		}
	}

	// If not authenticated or refresh failed, login as admin
	try {
		await serverPb.admins.authWithPassword(POCKETBASE_ADMIN_EMAIL, POCKETBASE_ADMIN_PASSWORD);
		console.log('New server authentication successful');
		return serverPb;
	} catch (error) {
		console.error('Server authentication failed:', error);
		throw error;
	}
}
