<script lang="ts">
  import api from '../api'
  import { beforeUpdate, onDestroy, onMount } from 'svelte'
  import Fa from 'svelte-fa'
  import { faBox, faBoxOpen, faClock, faMemory, faMicrochip, faNetworkWired, faPlay, faStop, faSync, faTag, faTags, faTerminal } from '@fortawesome/free-solid-svg-icons'
  import { messageBus } from '../messages/message-store'
  import { bytes2human, fmtDate, round } from './utils'

  export let enable_actions: boolean
  export let container_id: string
  let oldContainerId: string

  let intervalHandler: number | undefined
  let loading: boolean = true
  let runningAction: null | 'start' | 'stop' | 'restart' = null

  let container: ContainerInfoLong
  $: mem_perc = ((container?.mem?.used || 0) * 100) / (container?.mem?.total || 0)
  $: peak_mem_perc = ((container?.mem?.max_used || 0) * 100) / (container?.mem?.total || 0)
  $: image_name = container?.image.name.includes(':') ? container?.image.name.slice(0, container?.image.name.lastIndexOf(':')) : container?.image.name
  $: image_tag = container?.image.name.includes(':') ? container?.image.name.split(':').pop() : 'latest'

  beforeUpdate(() => {
    if (container_id !== oldContainerId) {
      oldContainerId = container_id
      loading = true
      runningAction = null
      if (container_id) api.send('get_container_info', { container_id })
    }
  })

  onMount(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    api.register<ContainerInfoLong>(
      'get_container_info',
      (info) => {
        if (info.id === container_id) {
          container = info
          loading = false
        }
      },
      (err) => messageBus.add({ text: err, type: 'error' }),
    )

    api.register<void>(
      'set_container_state',
      () => {
        runningAction = null
      },
      (err) => messageBus.add({ text: err, type: 'error' }),
    )

    intervalHandler = setInterval(() => {
      api.send('get_container_info', { container_id })
    }, 3000)
  })

  onDestroy(() => {
    clearInterval(intervalHandler)
    api.unregister('get_container_info')
    api.unregister('set_container_state')
  })

  function sendAction(action: 'start' | 'restart' | 'stop') {
    api.send('set_container_state', { container_id, action })
    runningAction = action
    switch (action) {
      case 'start':
        messageBus.add({ text: 'Starting container ...', type: 'success' })
        break
      case 'restart':
        messageBus.add({ text: 'Restarting container ...', type: 'info' })
        break
      case 'stop':
        messageBus.add({ text: 'Stopping container ...', type: 'info' })
        break
    }
  }
</script>

<div>
  {#if loading}
    <div class="d-flex align-items-center">
      <strong>Loading...</strong>
      <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
    </div>
  {:else}
    <div class="d-flex mb-3">
      <div class="icon-left ms-1 me-3">
        <Fa icon={faBoxOpen} size="2x" />
      </div>
      <div class="d-flex flex-column flex-grow-1">
        <div class="flex-grow-1 d-flex align-items-center justify-content-between">
          <div class="flex-grow-1">
            <div class="mb-1">
              <span class="me-2">Container</span>
              <span class="text-muted font-monospace">#{container.id.substring(0, 12)}</span>
            </div>
            <div>
              <h6>{container.name.replace(/^\//, '')}</h6>
            </div>
          </div>
          {#if enable_actions}
            <div class="ms-4">
              {#if container.status === 'running'}
                {#if !runningAction || runningAction === 'restart'}
                  <button type="button" class="btn btn-outline-warning" disabled={!!runningAction} on:click={() => sendAction('restart')}>
                    {#if !runningAction}
                      <Fa icon={faSync} />
                    {:else}
                      <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                    {/if}
                    Restart
                  </button>
                {/if}
                {#if !runningAction || runningAction === 'stop'}
                  <button type="button" class="btn btn-outline-danger" disabled={!!runningAction} on:click={() => sendAction('stop')}>
                    {#if !runningAction}
                      <Fa icon={faStop} />
                    {:else}
                      <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                    {/if}
                    Stop
                  </button>
                {/if}
              {:else if !runningAction || runningAction === 'start'}
                <button type="button" class="btn btn-outline-success" disabled={!!runningAction} on:click={() => sendAction('start')}>
                  {#if !runningAction}
                    <Fa icon={faPlay} />
                  {:else}
                    <span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                  {/if}
                  Start
                </button>
              {/if}
            </div>
          {/if}
        </div>
        <div>
          <Fa icon={faTerminal} />
          <code>{container.command}</code>
        </div>
      </div>
    </div>

    <div class="d-flex mb-3">
      <div class="icon-left ms-1 me-3">
        <Fa icon={faBox} size="2x" />
      </div>
      <div class="flex-grow-1">
        <div class="mb-1">
          <span class="me-2">Image</span>
          {#if container.image?.hash !== container?.image?.name}
            <span class="text-muted font-monospace">{container.image.hash.substring(0, 12 + 7)}</span>
          {/if}
        </div>
        <div>
          <h6>
            {#if !image_name.includes('/')}
              <a href="https://hub.docker.com/_/{image_name}" target="_blank" rel="noopener noreferrer" class="text-decoration-none">{image_name}</a>
            {:else if image_name.match(/^\w+\/\w+$/)}
              <a href="https://hub.docker.com/r/{image_name}" target="_blank" rel="noopener noreferrer" class="text-decoration-none">{image_name}</a>
            {:else}
              {image_name}
            {/if}
            <span class="ms-1">
              <Fa icon={faTag} />
              {image_tag}
            </span>
          </h6>
        </div>
      </div>
    </div>

    {#if container.cpu}
      <div class="d-flex mb-3">
        <div class="icon-left ms-1 me-3">
          <Fa icon={faMicrochip} size="2x" />
        </div>
        <div class="flex-grow-1">
          <div class="mb-1">Processor</div>
          <div class="progress">
            <div class="progress-bar text-white overflow-visible ps-1" style="width: {container.cpu.perc}%">
              {round(container.cpu.perc)}%
            </div>
          </div>
        </div>
      </div>
    {/if}

    {#if container.mem}
      <div class="d-flex mb-3">
        <div class="icon-left ms-1 me-3">
          <Fa icon={faMemory} size="2x" />
        </div>
        <div class="flex-grow-1">
          <div class="mb-1">
            <span class="me-2">Memory</span>
            {#if container.mem.used !== null}
              <span class="badge rounded-pill bg-primary ms-2">Now {bytes2human(container.mem.used)}</span>
            {/if}
            {#if container.mem.max_used !== null}
              <span class="badge rounded-pill bg-warning ms-2">Max {bytes2human(container.mem.max_used)}</span>
            {/if}
            {#if container.mem.total !== null}
              <span class="badge rounded-pill bg-info ms-2">Limit {bytes2human(container.mem.total)} </span>
            {/if}
          </div>
          {#if container.mem.used !== null && container.mem.total !== null}
            <div class="progress">
              <div class="progress-bar text-white overflow-visible ps-1" style="width: {mem_perc}%; z-index: 2">
                {round(mem_perc)}%
              </div>
              {#if container.mem.max_used !== null}
                <div class="progress-bar progress-bar-striped bg-warning" style="width: {peak_mem_perc - mem_perc}%"></div>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    {/if}

    {#if container.net || container.ports?.length > 0}
      <div class="d-flex mb-3">
        <div class="icon-left ms-1 me-3">
          <Fa icon={faNetworkWired} size="2x" />
        </div>
        {#if container.net}
          <div class="me-5">
            <div class="mb-1">Network</div>
            <span title="Received Traffic" class="me-3">▼ {bytes2human(container.net.rx_bytes)}</span>
            <span title="Sent Traffic">▲ {bytes2human(container.net.tx_bytes)}</span>
          </div>
        {/if}
        {#if container.ports?.length > 0}
          <div class="flex-grow-1">
            <div class="mb-1">Ports</div>
            {#each container.ports as port}
              <span class="badge bg-dark me-2">{port}</span>
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    <div class="d-flex mb-3">
      <div class="icon-left ms-1 me-3">
        <Fa icon={faClock} size="2x" />
      </div>
      <div class="flex-grow-1 pb-5 mb-5">
        <div class="mb-1">Timeline</div>
        <div class="timeline mt-2">
          <div class="tl-container" style="margin-left: 5%">
            <div class="popup">
              <div class="fw-bold">Created</div>
              {fmtDate(container.created_at)}
            </div>
          </div>
          <div class="tl-container" style="margin-left: 27%">
            <div class="popup">
              <div class="fw-bold">{container.crashes}</div>
              Crashes
            </div>
          </div>
          <div class="tl-container" style="margin-left: 49%">
            <div class="popup">
              {#if container.finished_at < container.started_at}
                <div class="fw-bold">Stopped</div>
                {#if container.finished_at < container.created_at}
                  Never
                {:else}
                  {fmtDate(container.finished_at)}
                {/if}
              {:else}
                <div class="fw-bold">Started</div>
                {fmtDate(container.started_at)}
              {/if}
            </div>
          </div>
          <div class="tl-container" style="margin-left: 71%">
            <div class="popup">
              {#if container.finished_at > container.started_at}
                <div class="fw-bold">Stopped</div>
                {fmtDate(container.finished_at)}
              {:else}
                <div class="fw-bold">Started</div>
                {fmtDate(container.started_at)}
              {/if}
            </div>
          </div>
          <div class="tl-container" style="margin-left: 93%">
            <div class="popup">
              Currently
              <div class="fw-bold">{container.status.charAt(0).toUpperCase() + container.status.slice(1).toLowerCase()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {#if container.env || container.labels}
      <div class="d-flex mb-3">
        <div class="icon-left ms-1 me-3">
          <Fa icon={faTags} size="2x" />
        </div>
        <div class="flex-grow-1 d-lg-flex" style="font-size: small">
          <div>
            <table class="table table-striped border">
              <thead>
                <tr>
                  <th scope="col" colspan="2" style="font-weight: normal">Environment Variables</th>
                </tr>
              </thead>
              <tbody>
                {#each Object.entries(container.env).sort(([key1], [key2]) => key1.localeCompare(key2)) as [key, value]}
                  <tr>
                    <td class="text-end border-end text-break">
                      {key}
                    </td>
                    <td class="text-break">
                      {value}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          <div>
            <table class="table table-striped border">
              <thead>
                <tr>
                  <th scope="col" colspan="2" style="font-weight: normal">Labels</th>
                </tr>
              </thead>
              <tbody>
                {#each Object.entries(container.labels).sort(([key1], [key2]) => key1.localeCompare(key2)) as [key, value]}
                  <tr>
                    <td class="text-end border-end text-break">
                      {key}
                    </td>
                    <td class="text-break">
                      {value}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .timeline {
    position: relative;
    height: 0.5rem;
    border-radius: 0.25rem;
    word-wrap: normal;

    background-color: #e9ecef;
  }

  :global(html.dark) .timeline {
    background-color: #3b3b3b;
  }

  .timeline .tl-container::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: #666;
    border: 4px solid #ff9f55;
    top: -6px;
    border-radius: 50%;
    z-index: 1;
  }

  .timeline .popup {
    position: absolute;
    margin-top: 1rem;
    margin-left: -2rem;
    width: 5rem;
    text-align: center;
  }

  .icon-left {
    width: 2.75rem;
    color: gray;
  }
</style>
