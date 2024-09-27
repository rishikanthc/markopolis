import PocketBase from 'pocketbase';
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Client-side PocketBase instance
export const pb = new PocketBase('http://127.0.0.1:8090'); // Replace with your PocketBase URL

export const currentUser = writable(pb.authStore.model);

if (browser) {
	pb.authStore.onChange((auth) => {
		console.log('Client AuthStore changed', auth);
		currentUser.set(pb.authStore.model);
	});
}

export async function login(email: string, password: string) {
	try {
		const authData = await pb.admins.authWithPassword(email, password);
		console.log('Logged in successfully', authData);
		return authData;
	} catch (error) {
		console.error('Login failed', error);
		throw error;
	}
}

export function logout() {
	pb.authStore.clear();
}
