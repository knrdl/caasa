<script lang="ts">
  import Fa from "svelte-fa"
  import {faCog} from "@fortawesome/free-solid-svg-icons"

  export let btnClass: string = 'secondary'
</script>

<div class="dropdown">
    <button class="btn btn-{btnClass} dropdown-toggle" type="button">
        <slot name="button">
            <Fa icon={faCog}/>
        </slot>
    </button>
    <ul class="dropdown-menu">
        <slot></slot>
    </ul>
</div>

<style>
    .dropdown-toggle:focus {
        pointer-events: none;
    }

    .dropdown-toggle:focus + .dropdown-menu {
        opacity: 1;
        visibility: visible;
        pointer-events: auto;
    }

    .dropdown-menu {
        opacity: 0;
        display: block;
        visibility: hidden;
        transition: visibility 0.5s;
        right: 0;
    }
</style>
