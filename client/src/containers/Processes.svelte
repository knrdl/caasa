<script lang="ts">
    import api from "../api";
    import {beforeUpdate, onDestroy, onMount} from "svelte";
    import Fa from "svelte-fa";
    import {faLevelUpAlt} from "@fortawesome/free-solid-svg-icons";
    import {messageBus} from "../messages/message-store";

    export let container_id: string
    let oldContainerId: string
    let logElem: HTMLPreElement

    let intervalHandler
    let loading: boolean = true
    let procs: Proc[] = null

    beforeUpdate(() => {
        if (container_id !== oldContainerId) {
            oldContainerId = container_id
            loading = true
            procs = null
            if (container_id)
                api.send('get_processes', {container_id})
        }
    })

    onMount(() => {
        api.register<Proc[]>('get_processes', data => {
            procs = data
            loading = false
        }, (err) => messageBus.add({text: err, type: 'error'}))

        intervalHandler = setInterval(() => {
            api.send('get_processes', {container_id})
        }, 3000)
    })

    onDestroy(() => {
        clearInterval(intervalHandler)
        api.unregister('get_processes')
    })

    function fullscreen() {
        if (logElem.requestFullscreen) {
            logElem.requestFullscreen({navigationUI: 'show'})
        }
    }

    function valueOrDefault(value: any, fallback: any) {
        if (value !== null && value !== undefined) {
            return value
        } else {
            return fallback
        }
    }
</script>

<div style="overflow-x:scroll">
    {#if loading}
        <div class="d-flex align-items-center">
            <strong>Loading...</strong>
            <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
        </div>
    {:else}
        <table class="table table-striped">
            <thead>
            <tr>
                <th scope="col" class="text-end" title="Process ID">PID</th>
                <th scope="col" class="text-end" title="Processor Usage">CPU</th>
                <th scope="col" class="text-end">Memory</th>
                <th scope="col" class="text-center">Started At</th>
                <th scope="col" class="text-center">User</th>
                <th scope="col" class="text-start">Command</th>
            </tr>
            </thead>
            <tbody>
            {#each (procs || []) as proc}
                <tr>
                    <td class="text-end">
                        {proc.pid}
                    </td>
                    <td class="text-end">
                        {#if valueOrDefault(proc['%cpu'], null)}
                            {proc['%cpu']}%
                        {/if}
                    </td>
                    <td class="text-end">
                        {#if valueOrDefault(proc['%mem'], null)}
                            {proc['%mem']}%
                        {/if}
                    </td>
                    <td class="text-center">
                        {valueOrDefault(proc.stime, '')}
                    </td>
                    <td class="text-center">
                        {valueOrDefault(proc.user, '')}
                    </td>
                    <td class="text-start">
                        <div class="d-flex">
                            {#each Array(proc.level) as _, i}
                                <div style="width: 2rem" class="me-2 d-flex justify-content-end align-items-center">
                                    {#if proc.level === i + 1}
                                        <Fa icon={faLevelUpAlt} rotate={90}/>
                                    {/if}
                                </div>
                            {/each}
                            <div class="font-monospace">
                                {proc.command}
                            </div>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    {/if}
</div>

<style>

</style>
