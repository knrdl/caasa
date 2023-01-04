<script lang="ts">
    import api from "../api"
    import LoadingScreen from "../LoadingScreen.svelte"
    import {onDestroy, onMount} from "svelte"
    import {fly, slide} from 'svelte/transition'
    import Dashboard from "./Dashboard.svelte"
    import LogViewer from "./LogViewer.svelte"
    import Filesystem from "./Filesystem.svelte"
    import Processes from "./Processes.svelte"
    import Terminal from "./Terminal.svelte"
    import SystemInfo from "./SystemInfo.svelte"
    import {messageBus} from "../messages/message-store"
    import ContainerList from "./ContainerList.svelte"

    let intervalHandler
    let loading: boolean = true
    let containers: ContainerInfoShort[]
    let selectedContainer: ContainerInfoShort
    export let showHostInfo: boolean
    export let showContainerListOverlay: boolean
    let tab: Tab = null

    onMount(() => {
        api.register<ContainerInfoShort[]>('get_container_list', list => {
            containers = list
            loading = false
        }, (err) => messageBus.add({text: err, type: 'error'}))

        api.send('get_container_list')
        intervalHandler = setInterval(() => {
            api.send('get_container_list')
        }, 3000)
    })

    onDestroy(() => {
        api.unregister('get_container_list')
        clearInterval(intervalHandler)
    })

    function selectContainer(container: ContainerInfoShort) {
        tab = null
        showHostInfo = false
        showContainerListOverlay = false
        selectedContainer = null
        window.scrollTo({top: 0, behavior: 'smooth'})
        setTimeout(() => {
            selectedContainer = container
            const perms: Tab[] = ['info', 'logs', 'procs', 'term', 'files']
            for (let perm of perms) {
                if (selectedContainer?.permissions?.includes(perm)) {
                    tab = perm
                    break
                }
            }
            if (!tab) {
                selectedContainer = null
                messageBus.add({type: 'warning', text: 'No permissions to access container'})
            }
        }, 100)
    }

    function selectTab(newTab: Tab) {
        tab = newTab
    }

    $: isSelectedContainerRunning = selectedContainer?.status === 'running'

</script>

{#if loading}
    <LoadingScreen/>
{/if}
<div class="d-md-none position-relative" style="z-index: 100;" class:d-none={!showContainerListOverlay}>
    <div class="position-fixed top-0 bottom-0 start-0 end-0" style="background: rgba(0, 0, 0, .55);"
         on:click={()=>showContainerListOverlay = false}></div>
    {#if showContainerListOverlay}
        <div class="position-absolute" transition:fly="{{ y: -50, duration: 200 }}">
            <ContainerList on:select-container={e => selectContainer(e.detail)} {containers}
                           selectedContainer={showHostInfo ? null : selectedContainer}/>
        </div>
    {/if}
</div>
<div class="d-flex pb-3 align-items-start">
    <aside class="d-none d-md-block me-4">
        <ContainerList on:select-container={e => selectContainer(e.detail)} {containers}
                       selectedContainer={showHostInfo ? null : selectedContainer}/>
    </aside>
    {#if showHostInfo}
        <SystemInfo/>
    {:else}
        <div class="container-md" transition:fly="{{ x: 300, duration: 200 }}" style="overflow: hidden">
            <div class="card tabs">
                <ul class="card-header">
                    {#if selectedContainer?.permissions?.includes('info')}
                        <li>
                            <button type="button" class:active={tab === 'info'} class="text-uppercase"
                                    on:click={() => selectTab('info')}>
                                Info
                            </button>
                        </li>
                    {/if}
                    {#if selectedContainer?.permissions?.includes('logs')}
                        <li>
                            <button type="button" class:active={tab === 'logs'} class="text-uppercase"
                                    on:click={() => selectTab('logs')}>
                                Logs
                            </button>
                        </li>
                    {/if}
                    {#if isSelectedContainerRunning && selectedContainer?.permissions?.includes('term')}
                        <li>
                            <button type="button" class:active={tab === 'term'} class="text-uppercase"
                                    on:click={() => selectTab('term')}>
                                Terminal
                            </button>
                        </li>
                    {/if}
                    {#if isSelectedContainerRunning && selectedContainer?.permissions?.includes('procs')}
                        <li>
                            <button type="button" class:active={tab === 'procs'} class="text-uppercase"
                                    on:click={() => selectTab('procs')}>
                                Processes
                            </button>
                        </li>
                    {/if}
                    {#if isSelectedContainerRunning && selectedContainer?.permissions?.includes('files')}
                        <li>
                            <button type="button" class:active={tab === 'files'} class="text-uppercase"
                                    on:click={() => selectTab('files')}>
                                Files
                            </button>
                        </li>
                    {/if}
                </ul>
                <div class="card-body py-4">
                    {#if tab === 'info'}
                        <div in:slide|local>
                            <Dashboard container_id={selectedContainer.id}
                                       enable_actions={selectedContainer.permissions.includes('state')}/>
                        </div>
                    {:else if tab === 'logs'}
                        <div in:slide|local>
                            <LogViewer container_id={selectedContainer.id}/>
                        </div>
                    {:else if tab === 'term'}
                        <div in:slide|local>
                            <Terminal container_id={selectedContainer.id}/>
                        </div>
                    {:else if tab === 'procs'}
                        <div in:slide|local>
                            <Processes container_id={selectedContainer.id}/>
                        </div>
                    {:else if tab === 'files'}
                        <div in:slide|local>
                            <Filesystem container_id={selectedContainer.id}
                                        allow_download={selectedContainer.permissions.includes('files-read')}
                                        allow_upload={selectedContainer.permissions.includes('files-write')}
                            />
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
</style>

