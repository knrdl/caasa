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

    let loggedInUsername: string | null = null
    let userCanLogout: boolean = true
    let showHostInfo: boolean = true

    onMount(async () => {
        api.register('ws-error', null, (err) => messageBus.add({text: err, type: 'error'}))
        api.register('ws-close', null, (err) => {
            messageBus.add({text: err, type: 'error'})
            loggedInUsername = null
            alert('Lost connection. Reconnect?')
            window.location.reload()
        })
        api.register<{ username: string }>('webproxy_auth', ({username}) => {
            loggedInUsername = username
            userCanLogout = false
        }, err => {
            messageBus.add({text: err, type: 'error'})
        })
        await api.init()
    })

    function logout() {
        api.close()
        loggedInUsername = null
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
            {#if loggedInUsername && userCanLogout}
                <button type="button" class="btn mx-2" on:click={logout} title="Logout {loggedInUsername}">
                    <Fa icon={faSignOutAlt} color="#333" size="2x"/>
                </button>
            {/if}
        </div>
    </header>
    {#if loggedInUsername}
        <Index bind:showHostInfo={showHostInfo}/>
    {:else}
        <Login on:login={({username}) => loggedInUsername = username}/>
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
