import PocketBase from 'pocketbase';
import { env } from '$env/dynamic/private';
import type { Handle } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { redirect } from '@sveltejs/kit';

export const authentication: Handle = async ({ event, resolve }) => {
	event.locals.pb = new PocketBase('http://localhost:8090');
	// Load the store data from the request cookie string
	const cookieHeader = event.request.headers.get('cookie') || '';
	console.log('Received cookie:', cookieHeader);
	event.locals.pb.authStore.loadFromCookie(cookieHeader, 'pb_auth');
	console.log('Auth state after loading cookie:', event.locals.pb.authStore.isValid);
	console.log('Auth token:', event.locals.pb.authStore.token);

	try {
		// Get an up-to-date auth store state by verifying and refreshing the loaded auth model (if any)
		if (event.locals.pb.authStore.isValid) {
			await event.locals.pb.collection('users').authRefresh();
			console.log('Auth state after refresh:', event.locals.pb.authStore.isValid);
		}
	} catch (err) {
		// Clear the auth store on failed refresh
		console.error('Auth refresh failed:', err);
		event.locals.pb.authStore.clear();
	}

	const response = await resolve(event);

	// Send back the auth cookie to the client with the latest store state
	const cookie = event.locals.pb.authStore.exportToCookie({
		httpOnly: true,
		secure: process.env.NODE_ENV === 'production',
		sameSite: 'lax',
		path: '/'
	});
	response.headers.append('Set-Cookie', cookie);
	console.log('Cookie being set:', cookie);

	return response;
};

export const authorization: Handle = async ({ event, resolve }) => {
	// Protect the route under /dashboard
	if (event.url.pathname.startsWith('/login/success')) {
		console.log('Dashboard request detected');
		const loggedIn = event.locals.pb.authStore.isValid;
		console.log('Dashboard access attempt. Auth state:', loggedIn);
		console.log('Auth token for dashboard request:', event.locals.pb.authStore.token);
		if (!loggedIn) {
			console.log('User not authenticated, redirecting to login');
			throw redirect(303, '/login');
		} else {
			console.log('User authenticated, proceeding to dashboard');
		}
	}
	return resolve(event);
};

export const handle = sequence(authentication, authorization);
