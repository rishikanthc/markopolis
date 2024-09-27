import type { PageServerLoad, Actions } from './$types.js';
import { fail, redirect } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { formSchema } from '$lib/components/schema';

export const load: PageServerLoad = async () => {
	return {
		form: await superValidate(zod(formSchema))
	};
};

export const actions: Actions = {
	default: async (event) => {
		const data = await superValidate(event, zod(formSchema));
		if (!data.valid) {
			return fail(400, {
				data
			});
		}
		console.log(data);
		const email = data.data.username;
		const password = data.data.password;
		console.log('Login action called');
		if (!email || !password) {
			return fail(400, { emailRequired: !email, passwordRequired: !password });
		}
		try {
			const authData = await event.locals.pb.collection('users').authWithPassword(email, password);
			console.log('Logged in successfully. Auth state:', event.locals.pb.authStore.isValid);

			// Ensure the auth data is saved to the auth store
			event.locals.pb.authStore.save(authData.token, authData.record);

			// Set the auth cookie
			const cookieOptions = {
				httpOnly: true,
				secure: process.env.NODE_ENV === 'production',
				sameSite: 'lax',
				path: '/',
				maxAge: 60 * 60 * 24 * 30 // 30 days
			};
			const cookie = event.locals.pb.authStore.exportToCookie(cookieOptions);

			console.log('Auth state before redirect:', event.locals.pb.authStore.isValid);
			console.log('Attempting to redirect to /dashboard');

			// Use throw redirect instead of return
			// throw redirect(303, '/login/success');
		} catch (error) {
			console.error('Login error:', error);
			const errorObj = error as ClientResponseError;
			return fail(500, { form: data });
		}

		throw redirect(303, '/login/success');
		/* return {
			form
		}; */
	}
};
