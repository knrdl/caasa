<script lang="ts">
    import api from "../api";
    import {onDestroy, onMount} from "svelte";
    import Fa from "svelte-fa";
    import {faBoxOpen, faMemory, faMicrochip, faServer} from "@fortawesome/free-solid-svg-icons";
    import {faDocker} from "@fortawesome/free-brands-svg-icons";
    import {messageBus} from "../messages/message-store";
    import {bytes2human} from "./utils";

    let loading: boolean = true
    let info: SysInfo

    onMount(() => {
        api.register<SysInfo>('get_system_info', result => {
            info = result
            loading = false
        }, (err) => {
            loading = false
            messageBus.add({text: err, type: 'error'})
        })
        api.send('get_system_info')
    })

    onDestroy(() => {
        api.unregister('get_system_info')
    })
</script>

<div class="flex-grow-1 d-flex justify-content-center align-items-start mt-5">
    {#if loading}
        <div class="d-flex align-items-center">
            <strong class="mx-5">Loading...</strong>
            <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
        </div>
    {:else if info}
        <div class="card">
            <div class="card-body">
                <div class="fs-4 text-uppercase mb-3">Host</div>
                <div class="d-flex align-items-center mb-2">
                    <Fa icon={faServer} size="lg" style="width: 3rem"/> {info.os}
                </div>
                <div class="d-flex align-items-center mb-2">
                    <Fa icon={faMicrochip} size="lg" style="width: 3rem"/> {info.cpus} CPUs
                </div>
                <div class="d-flex align-items-center mb-2">
                    <Fa icon={faMemory} size="lg" style="width: 3rem"/> {bytes2human(info.mem)}
                    Memory
                </div>
                <div class="d-flex align-items-center mb-2">
                    <Fa icon={faDocker} size="lg" style="width: 3rem"/>
                    Docker {info.version}
                </div>
                <div class="d-flex align-items-center mb-2">
                    <Fa icon={faBoxOpen} size="lg" style="width: 3rem"/>
                    {info.containers.running}/{info.containers.total} Containers running
                </div>
            </div>
        </div>
    {/if}
</div>

<style>

</style>
