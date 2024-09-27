import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
	console.log('Dashboard load function. Auth state:', locals.pb.authStore.isValid);

	if (!locals.pb.authStore.isValid) {
		console.log('User not authenticated, redirecting to login');
		throw redirect(303, '/login');
	}

	// You can fetch additional data for the dashboard here
	return {
		user: locals.pb.authStore.model
	};
};
