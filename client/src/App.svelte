<script lang="ts">
    import MessageQueue from "./messages/MessageQueue.svelte"
    import ThemeSwitcher from "./ThemeSwitcher.svelte"
    import Login from "./auth/Login.svelte"
    import {onMount} from "svelte"
    import api from "./api"
    import {messageBus} from "./messages/message-store"
    import Index from "./containers/Index.svelte"
    import Fa from "svelte-fa"
    import {faHouseUser, faSignOutAlt} from "@fortawesome/free-solid-svg-icons"

    let isUserLoggedIn: boolean = false
    let showHostInfo: boolean = true

    onMount(async () => {
        api.register('ws-error', null, (err) => messageBus.add({text: err, type: 'error'}))
        api.register('ws-close', null, (err) => {
            messageBus.add({text: err, type: 'error'})
            isUserLoggedIn = false
            alert('Lost connection. Reconnect?')
            window.location.reload()
        })
        await api.init()
    })

    function logout() {
        api.close()
        isUserLoggedIn = false
        messageBus.add({text: 'Logged out', type: 'info'})
        window.location.reload()
    }

    function handleAppError() {
        alert('An error occurred!')
    }

</script>

<svelte:window on:error={handleAppError}/>

<MessageQueue/>

<main>
    <header>
        <a href="/#/" class="d-flex justify-content-center align-items-center"
           on:click|preventDefault={()=>showHostInfo=true}>
            <Fa icon={faHouseUser} color="#123" size="2x" style="width: 3rem;height: 3rem;"/>
            <span class="text-black ps-2 fs-2 fw-light">
                    Container as a Service Admin
                </span>
        </a>
        <div class="items-right">
            <ThemeSwitcher/>
            {#if isUserLoggedIn}
                <button type="button" class="btn mx-2" on:click={logout} title="Logout">
                    <Fa icon={faSignOutAlt} color="#333" size="2x"/>
                </button>
            {/if}
        </div>
    </header>
    {#if isUserLoggedIn}
        <Index bind:showHostInfo={showHostInfo}/>
    {:else}
        <Login on:login={() => isUserLoggedIn = true}/>
    {/if}
</main>

<style>

    header {
        box-shadow: 5px -5px 8px 10px rgba(0, 0, 0, .25);
        background: linear-gradient(to right, rgb(14, 101, 173), rgb(109, 152, 74));
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1rem 1rem 1.5rem;
        margin-bottom: 1rem;
    }

    header a {
        text-decoration: none;
    }

    header .items-right {
        display: flex;
        align-items: center;
    }

    main {
        min-height: 100vh;
    }

    :global(html:not(.dark)) main {
        background-color: #eee;
    }
</style>
