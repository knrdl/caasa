<script lang="ts">
    import {messageBus} from "./message-store";
    import {onMount} from "svelte";
    import {slide} from 'svelte/transition';

    let msgs: Message[] = []

    onMount(() => {
        messageBus.subscribe((store) => msgs = store)
    })
</script>

<div class="position-fixed bottom-0 end-0 p-3" style="z-index: 470">

    {#each msgs as msg}
        <div class="toast show align-items-center text-white border-0 mb-2"
             class:bg-danger={msg.type === 'error'}
             class:bg-warning={msg.type === 'warning'}
             class:bg-success={msg.type === 'success'}
             class:bg-primary={msg.type === 'info'}
             transition:slide|local>
            <div class="d-flex">
                <div class="toast-body">
                    {msg.text}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        on:click={() => messageBus.remove(msg)}></button>
            </div>
        </div>
    {/each}
</div>

<style>

</style>
