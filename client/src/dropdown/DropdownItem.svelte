<script lang="ts">
  export let active: boolean = false
</script>

<li>
  <button class="dropdown-item" class:active="{active}" type="button" on:click>
    <slot />
  </button>
</li>
