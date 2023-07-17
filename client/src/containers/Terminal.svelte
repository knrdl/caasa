<script lang="ts">
  import 'xterm/css/xterm.css'

  import { beforeUpdate, onDestroy, onMount, tick } from 'svelte'
  import { Terminal as XTerm } from 'xterm'
  import { FitAddon } from 'xterm-addon-fit'
  import api from '../api'
  import { messageBus } from '../messages/message-store'
  import { slide } from 'svelte/transition'
  import Fa from 'svelte-fa'
  import { faExpandArrowsAlt, faLaptopCode, faWindowClose } from '@fortawesome/free-solid-svg-icons'

  export let container_id: string
  let oldContainerId: string

  let terminalContainer: HTMLDivElement

  let isTerminalOpen: boolean = false
  const defaultCmd = 'sh'
  let cmd: string = defaultCmd
  const defaultUser = 'root'
  let user: string = defaultUser

  const term = new XTerm({ theme: { background: '#222', cursor: 'white', cursorAccent: '#222' }, cursorBlink: true })
  const fitAddon = new FitAddon()

  beforeUpdate(() => {
    if (container_id !== oldContainerId) {
      if (isTerminalOpen) {
        api.send('close_terminal')
        forceCloseTerm()
      }
      oldContainerId = container_id
    }
  })

  onMount(() => {
    api.register<void>(
      'spawn_terminal',
      () => {
        resizeTerm()
        term.focus()
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
    api.register<void>(
      'close_terminal',
      () => {
        messageBus.add({ text: 'Terminal has been closed', type: 'info' })
        forceCloseTerm()
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
    api.register<{ payload: null; blob: Blob }>(
      'receive_terminal_output',
      async (response) => {
        term.write(new Uint8Array(await response.blob.arrayBuffer()))
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )

    term.onResize((dat: { rows: number; cols: number }) => {
      api.send('resize_terminal', dat)
    })
    term.loadAddon(fitAddon)

    term.onData((data) => {
      api.send('transmit_terminal_input', { data })
    })
  })

  onDestroy(() => {
    if (isTerminalOpen) api.send('close_terminal')
    api.unregister('spawn_terminal')
    api.unregister('close_terminal')
    api.unregister('receive_terminal_output')
  })

  function resizeTerm() {
    if (isTerminalOpen) {
      fitAddon.fit()
    }
  }

  async function openTerm() {
    isTerminalOpen = true
    api.send('spawn_terminal', { container_id, cmd, user })
    await tick()
    term.open(terminalContainer)
  }

  function forceCloseTerm() {
    isTerminalOpen = false
    term.reset()
    term.clear()
    cmd = defaultCmd
    user = defaultUser
  }

  function fullscreen() {
    if (terminalContainer?.requestFullscreen) {
      terminalContainer.requestFullscreen({ navigationUI: 'show' })
    }
  }
</script>

<svelte:window on:resize="{resizeTerm}" />

{#if isTerminalOpen}
  <div class="d-flex justify-content-end mb-2">
    <button type="button" class="btn mx-3" title="Fullscreen" on:click="{fullscreen}">
      <Fa icon="{faExpandArrowsAlt}" size="lg" color="#666" />
    </button>
    <button type="button" class="btn mx-3" title="Close Terminal" on:click="{() => api.send('close_terminal')}">
      <Fa icon="{faWindowClose}" size="lg" color="#666" />
    </button>
  </div>
  <div bind:this="{terminalContainer}" class="border" style="height: calc(100vh - 280px)"></div>
{:else}
  <form class="container login-form" on:submit|preventDefault="{openTerm}" transition:slide|local>
    <div class="container" style="max-width: 400px">
      <div class="form-floating mb-2">
        <input type="text" class="form-control" id="inpTerminalCmd" bind:value="{cmd}" />
        <label for="inpTerminalCmd">Command</label>
      </div>
      <div class="form-floating mb-2">
        <input type="text" class="form-control" id="inpTerminalUser" bind:value="{user}" />
        <label for="inpTerminalUser">User</label>
      </div>
      <div class="col-12">
        <button type="submit" class="btn btn-primary w-100">
          <Fa icon="{faLaptopCode}" />
          Open Terminal
        </button>
      </div>
    </div>
  </form>
{/if}
