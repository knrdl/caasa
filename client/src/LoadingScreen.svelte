<script lang="ts">
  import {blur} from 'svelte/transition'
  import {onMount} from "svelte"

  export let text: string = ''

  let visible: boolean = false
  onMount(() => {
    setTimeout(() => visible = true, 250)
  })
</script>

{#if visible}
    <div class="bg-outer position-fixed d-flex justify-content-center align-items-center top-0 start-0 end-0 bottom-0"
         in:blur>
        <div class="bg-inner d-flex flex-column rounded p-3">
            <div class="d-flex justify-content-center align-items-center">
                {#each [1, 2, 3] as n}
                    <div class="spinner-grow mx-2 text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                {/each}
            </div>
            {#if text}
                <div class="mt-4 text-light">{text}</div>
            {/if}
        </div>
    </div>
{/if}

<style>
    .bg-outer {
        background: rgba(0, 0, 0, .55);
        z-index: 600;
    }

    .bg-inner {
        font-size: 14pt;
    }

</style>
