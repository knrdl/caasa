<script lang="ts">
  import { createEventDispatcher } from 'svelte'

  export let containers: ContainerInfoShort[]
  export let selectedContainer: ContainerInfoShort | null

  const dispatch = createEventDispatcher()

  let search: string = ''

  $: filteredContainers = containers?.filter(
    (container) =>
      container.name.toLowerCase().replace(/\s+/g, '').includes(search.replace(/\s+/g, '')) ||
      container.namespace?.toLowerCase().replace(/\s+/g, '').includes(search.replace(/\s+/g, '')),
  )
</script>

<aside class="d-flex flex-column pb-1">
  {#if containers}
    {#if containers.length === 0}
      <p class="mx-5 my-2">No containers found</p>
    {:else}
      <input type="search" class="form-control" placeholder="Search" value={search} on:input={(e) => (search = e.currentTarget.value.toLowerCase())} />
      {#each filteredContainers as container}
        {@const isSelected = selectedContainer && selectedContainer.id === container.id}
        <button
          type="button"
          class="btn d-flex border-top border-bottom"
          style="cursor: pointer; text-align: left"
          on:click={() => dispatch('select-container', container)}
          class:bg-dark={isSelected}
          class:text-light={isSelected}
        >
          <div
            class:bg-success={container.status === 'running'}
            class:bg-danger={['exited', 'dead', 'removing'].includes(container.status)}
            class:bg-warning={['created', 'paused', 'restarting'].includes(container.status)}
            style="width: 10px; flex: none"
          ></div>
          <div class="p-2 pe-4">
            <div class:text-muted={selectedContainer?.id !== container.id} class="text-uppercase">{container.namespace || ''}</div>
            <div>{container.name}</div>
          </div>
        </button>
      {:else}
        <p class="mx-2 my-1">No containers match search term</p>
      {/each}
    {/if}
  {/if}
</aside>

<style>
  input[type='search'] {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  aside {
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    background-color: var(--bs-body-bg);
    box-shadow: 5px 8px 17px 9px rgb(0 0 0 / 25%);
  }

  :global(html.dark) aside {
    background-color: var(--bs-body-bg-alt);
  }
</style>
