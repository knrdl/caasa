<script lang="ts">
  import api from '../api'
  import { beforeUpdate, onDestroy, onMount, tick } from 'svelte'
  import stripAnsi from 'strip-ansi'
  import Fa from 'svelte-fa'
  import { faChevronCircleDown, faChevronCircleUp, faDownload, faExpandArrowsAlt } from '@fortawesome/free-solid-svg-icons'
  import { messageBus } from '../messages/message-store'
  import { downloadBlob } from './utils'

  export let container_id: string
  let oldContainerId: string
  let logElem: HTMLPreElement

  let intervalHandler: number | undefined
  let loading: boolean = true
  let logs: string[] = []

  let timestampMode: 'off' | 'local' | 'raw' = 'local'

  beforeUpdate(() => {
    if (container_id !== oldContainerId) {
      oldContainerId = container_id
      loading = true
      logs = []
      if (container_id) api.send('get_container_logs', { container_id })
    }
  })

  onMount(() => {
    api.register<string[]>(
      'get_container_logs',
      (loglines) => {
        loading = false
        if (loglines?.length > 0) {
          let scrollToBottom = !logs || (logElem && logElem.scrollTop >= logElem.scrollHeight - logElem.clientHeight)
          const totalLines = logs.length + loglines.length
          if (totalLines > 5000) {
            logs.slice(totalLines - 5000)
          }
          logs.push(...loglines.map((line) => stripAnsi(line)))
          if (scrollToBottom) tick().then(() => (logElem.scrollTop = logElem.scrollHeight))
        }
      },
      (err) => messageBus.add({ text: err, type: 'error' }),
    )

    intervalHandler = setInterval(() => {
      api.send('get_container_logs', { container_id, onlynew: true })
    }, 3000)
  })

  onDestroy(() => {
    clearInterval(intervalHandler)
    api.unregister('get_container_logs')
  })

  function fullscreen() {
    if (logElem?.requestFullscreen) {
      logElem.requestFullscreen({ navigationUI: 'show' })
    }
  }

  function downloadLogs() {
    downloadBlob(new Blob(logs, { type: 'text/plain' }), container_id + '.log')
  }

  function fmtTimestamp(value: string) {
    return new Date(value).toLocaleDateString(undefined, {
      weekday: 'short',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }
</script>

<div>
  {#if loading}
    <div class="d-flex align-items-center">
      <strong>Loading...</strong>
      <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
    </div>
  {:else if logs.length === 0}
    <p>No Log Output yet ...</p>
  {:else}
    <div class="d-flex justify-content-between align-items-center mb-2">
      <div>
        <select class="form-select" bind:value={timestampMode}>
          <option value="off">hide timestamps</option>
          <option value="local">local timestamps</option>
          <option value="raw">raw timestamps</option>
        </select>
      </div>
      <div>
        <button type="button" class="btn mx-1" title="Scroll to Top" on:click={() => (logElem.scrollTop = 0)}>
          <Fa icon={faChevronCircleUp} size="lg" color="#666" />
        </button>
        <button type="button" class="btn mx-1" title="Scroll to Bottom" on:click={() => (logElem.scrollTop = logElem.scrollHeight)}>
          <Fa icon={faChevronCircleDown} size="lg" color="#666" />
        </button>
        <button type="button" class="btn mx-1" title="Download shown log lines" on:click={downloadLogs}>
          <Fa icon={faDownload} size="lg" color="#666" />
        </button>
        <button type="button" class="btn mx-1" title="Fullscreen" on:click={fullscreen}>
          <Fa icon={faExpandArrowsAlt} size="lg" color="#666" />
        </button>
      </div>
    </div>
    <!-- this might look ugly but it is necessary because whitespaces are preserved in <pre> envs-->
    <pre bind:this={logElem} class="mb-0">{#each logs as line}{@const timestamp = line.substring(0, line.indexOf(' '))}{@const text = line.substring(line.indexOf(' ') + 1)}<span
          class="pe-3"
          >{#if timestampMode !== 'off'}<time datetime={timestamp} class="me-1 px-1"
              >{#if timestampMode === 'local'}{fmtTimestamp(timestamp)}{:else}{timestamp}{/if}</time
            >{/if}<span class="pe-3">{text}</span></span
        >{/each}</pre>
  {/if}
</div>

<style>
  pre {
    scroll-behavior: smooth;
    max-height: calc(100vh - 280px);
    outline: 1px solid #ccc9;
    padding: 0.1rem 0.1rem 0.25rem 0.1rem;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
  }

  pre > span {
    display: block;
  }

  pre > span:nth-child(even) {
    background-color: #99999923;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
  }

  pre time {
    display: inline-block;
    background-color: #99666615;
  }

  :global(html.dark) pre time {
    background-color: #cc999913;
  }

  :global(html.dark) pre {
    background-color: var(--bs-body-bg-alt);
  }

  :global(html:not(.dark)) pre {
    background-color: #eee;
  }
</style>
