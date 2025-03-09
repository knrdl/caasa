<script lang="ts">
  import { slide } from 'svelte/transition'

  export let type: Message['type']
  export let dismissible: boolean = false
  let dismissed: boolean = false
</script>

<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="check-circle-fill" fill="currentColor" viewBox="0 0 16 16">
    <path
      d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"
    ></path>
  </symbol>
  <symbol id="info-fill" fill="currentColor" viewBox="0 0 16 16">
    <path
      d="M8 16A8 8 0 1 0 8 0akeyof Message8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"
    ></path>
  </symbol>
  <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
    <path
      d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"
    ></path>
  </symbol>
</svg>

{#if !dismissed}
  <div
    class="alert d-flex align-items-center"
    class:alert-danger={type === 'error'}
    class:alert-warning={type === 'warning'}
    class:alert-success={type === 'success'}
    class:alert-info={type === 'info'}
    class:alert-dismissible={dismissible}
    role="alert"
    transition:slide|local
  >
    {#if type === 'error' || type === 'warning'}
      <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:">
        <use xlink:href="#exclamation-triangle-fill"></use>
      </svg>
    {:else if type === 'success'}
      <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Success:">
        <use xlink:href="#check-circle-fill"></use>
      </svg>
    {:else if type === 'info'}
      <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:">
        <use xlink:href="#info-fill"></use>
      </svg>
    {/if}
    <div>
      {#if type === 'error'}
        <strong>Error:</strong>
      {/if}
      <slot />
      {#if dismissible}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" on:click={() => (dismissed = true)}></button>
      {/if}
    </div>
  </div>
{/if}
