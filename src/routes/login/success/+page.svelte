<!-- src/routes/dashboard/+page.svelte -->
<script lang="ts">
	export let data;
</script>

<h1>Welcome to your dashboard, {data.user?.email}</h1>

<div>Logged in Successfully !!</div>
