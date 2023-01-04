<script lang="ts">
    import {onMount} from "svelte"
    import {messageBus} from "./messages/message-store"
    import Fa from "svelte-fa"
    import {faMoon, faSun} from "@fortawesome/free-solid-svg-icons"

    let theme: 'light' | 'dark'

    function toggle() {
        if (theme === 'light') {
            theme = 'dark'
            document.querySelector('html').classList.add('dark')
            // messageBus.add({text: 'Switching to dark theme', type: 'info'})
        } else {
            theme = 'light'
            document.querySelector('html').classList.remove('dark')
            // messageBus.add({text: 'Switching to light theme', type: 'info'})
        }
    }

    onMount(() => {
        // theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? 'dark' : 'light'
        theme = 'dark'  // todo: should dark theme always be the default? perhaps yes
        if (theme === 'dark') document.querySelector('html').classList.add('dark')
    })

</script>

<button type="button" class="btn mx-2" on:click={toggle} title="Switch Theme">
    {#if theme === 'dark'}
        <Fa icon={faMoon} color="#333" size="2x"/>
    {:else}
        <Fa icon={faSun} color="#333" size="2x"/>
    {/if}
</button>

<style>

</style>
