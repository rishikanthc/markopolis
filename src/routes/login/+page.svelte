<script>
	import LoginForm from '$lib/components/LoginForm.svelte';
	export let data;
	$: formData = data?.form;
</script>

<LoginForm bind:data={formData} />
