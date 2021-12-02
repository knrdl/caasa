<script lang="ts">
    import api from "../api"
    import {beforeUpdate, onDestroy, onMount, tick} from "svelte"
    import stripAnsi from "strip-ansi"
    import Fa from "svelte-fa"
    import {faChevronCircleDown, faChevronCircleUp, faExpandArrowsAlt} from "@fortawesome/free-solid-svg-icons"
    import {messageBus} from "../messages/message-store"

    export let container_id: string
    let oldContainerId: string
    let logElem: HTMLPreElement

    let intervalHandler
    let loading: boolean = true
    let logs: string = ''

    beforeUpdate(() => {
        if (container_id !== oldContainerId) {
            oldContainerId = container_id
            loading = true
            logs = ''
            if (container_id)
                api.send('get_container_logs', {container_id})
        }
    })

    onMount(() => {
        api.register<string>('get_container_logs', loglines => {
            logs += stripAnsi(loglines)
            loading = false
            if (loglines)
                scroll2bottom()
        }, (err) => messageBus.add({text: err, type: 'error'}))

        intervalHandler = setInterval(() => {
            api.send('get_container_logs', {container_id, onlynew: true})
        }, 3000)
    })

    onDestroy(() => {
        clearInterval(intervalHandler)
        api.unregister('get_container_logs')
    })

    function scroll2bottom() {
        tick().then(() => {
            logElem.scrollIntoView(true)
            logElem.scrollTop = logElem.scrollHeight
        })
    }

    function fullscreen() {
        if (logElem?.requestFullscreen) {
            logElem.requestFullscreen({navigationUI: 'show'})
        }
    }
</script>

<div>
    {#if loading}
        <div class="d-flex align-items-center">
            <strong>Loading...</strong>
            <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
        </div>
    {:else}
        {#if logs.length === 0}
            <p>No Log Output yet ...</p>
        {:else}
            <div class="d-flex justify-content-end mb-2">
                <button type="button" class="btn mx-1" title="Scroll to Top" on:click={() => logElem.scrollTop = 0}>
                    <Fa icon={faChevronCircleUp} size="lg" color="#666"/>
                </button>
                <button type="button" class="btn mx-1" title="Scroll to Bottom"
                        on:click={() => logElem.scrollTop = logElem.scrollHeight}>
                    <Fa icon={faChevronCircleDown} size="lg" color="#666"/>
                </button>
                <button type="button" class="btn mx-1" title="Scroll to Bottom" on:click={fullscreen}>
                    <Fa icon={faExpandArrowsAlt} size="lg" color="#666"/>
                </button>
            </div>
            <pre bind:this={logElem}>{logs}</pre>
        {/if}
    {/if}
</div>

<style>
    pre {
        scroll-behavior: smooth;
        max-height: calc(100vh - 300px);
        outline: 1px solid #ccc9;
    }

    :global(html.dark) pre {
        background-color: var(--bs-body-bg-alt);
    }

    :global(html:not(.dark)) pre {
        background-color: #eee;
    }

</style>
