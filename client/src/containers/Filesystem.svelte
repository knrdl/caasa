<script lang="ts">
  import { beforeUpdate, onDestroy, onMount } from 'svelte'
  import api from '../api'
  import Fa from 'svelte-fa'
  import { faExternalLinkSquareAlt, faFile, faFolder, faHdd, faHome, faPlus, faSync } from '@fortawesome/free-solid-svg-icons'
  import { messageBus } from '../messages/message-store'
  import Dropdown from '../dropdown/Dropdown.svelte'
  import DropdownItem from '../dropdown/DropdownItem.svelte'
  import { downloadBlob } from './utils'

  export let container_id: string
  export let allow_download: boolean
  export let allow_upload: boolean

  let fileUploadElem: HTMLInputElement

  let loading: boolean = true
  let oldContainerId: string
  let currentDir: string = '/'
  let currentEntries: DirectoryListing[] = null
  let info: FilesystemInfo = null

  beforeUpdate(() => {
    if (container_id !== oldContainerId) {
      oldContainerId = container_id
      loading = true
      currentDir = '/'
      currentEntries = null
      info = null
      if (container_id) api.send('get_filesystem_info', { container_id })
    }
  })

  onMount(() => {
    api.register<FilesystemInfo>(
      'get_filesystem_info',
      (response) => {
        loadPath(response.workdir)
        info = response
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
    api.register<{ path: string; entries: DirectoryListing[] }>(
      'get_directory_list',
      (response) => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
        currentEntries = response.entries
        currentDir = response.path
        loading = false
      },
      (err) => {
        messageBus.add({ text: err, type: 'error' })
        currentEntries = null
        loading = false
      }
    )
    api.register<{ payload: { path: string }; blob: Blob }>(
      'download_file',
      (response) => {
        downloadBlob(response.blob, response.payload.path.split('/').pop())
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
    api.register<void>(
      'create_folder',
      () => {
        loadPath(currentDir)
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
    api.register<void>(
      'upload_file',
      () => {
        loadPath(currentDir)
      },
      (err) => messageBus.add({ text: err, type: 'error' })
    )
  })

  onDestroy(() => {
    api.unregister('get_filesystem_info')
    api.unregister('get_directory_list')
    api.unregister('create_folder')
    api.unregister('upload_file')
    api.unregister('download_file')
  })

  function gotoSubDir(subdir: string) {
    let dir = currentDir
    if (!dir.endsWith('/')) dir += '/'
    dir += subdir
    loadPath(dir)
  }

  function loadPath(path: string) {
    currentDir = path
    api.send('get_directory_list', { container_id, path })
    loading = true
    currentEntries = null
  }

  function requestFileDownload(filename: string) {
    if (allow_download) api.send('download_file', { container_id, path: `${currentDir}/${filename}` })
  }

  function addFolder() {
    const folderName: string = prompt('Folder name:')
    if (folderName) {
      api.send('create_folder', { container_id, path: `${currentDir}/${folderName}` })
    }
  }

  async function uploadFile() {
    const toBase64 = (file) =>
      new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve((reader.result as string).split(',')[1])
        reader.onerror = (error) => reject(error)
      })

    const file = fileUploadElem.files[0]
    if (confirm(`Upload file "${file.name}"?`)) {
      api.send('upload_file', { container_id, path: `${currentDir}/${file.name}`, content: await toBase64(file) })
    }
  }

  $: parseCurrentDir = () => {
    const output = []
    const segments = currentDir.split('/')
    let totalPath = ''
    for (const segment of segments) {
      if (segment) {
        totalPath += '/' + segment
        output.push({ segment, totalPath })
      }
    }
    output.unshift({ segment: '/', totalPath: '/' })
    return output
  }
</script>

<div style="overflow-x:auto">
  {#if loading}
    <div class="d-flex align-items-center">
      <strong>Loading...</strong>
      <div class="spinner-border ms-auto" role="status" aria-hidden="true"></div>
    </div>
  {:else}
    <div class="d-flex justify-content-between align-items-center">
      <div class="d-flex">
        <div class="btn-group me-1">
          <button type="button" class="btn btn-outline-primary" on:click="{() => loadPath(info.workdir)}">
            <Fa icon="{faHome}" />
          </button>
          <button type="button" class="btn btn-outline-primary" on:click="{() => loadPath(currentDir)}">
            <Fa icon="{faSync}" />
          </button>
        </div>

        <div class="btn-group mx-2" role="group">
          {#each parseCurrentDir() as itm}
            <button type="button" class="btn btn-secondary border-dark" on:click="{() => loadPath(itm.totalPath)}">{itm.segment || '/'}</button>
          {/each}
        </div>
      </div>

      <div class="d-flex">
        {#if allow_upload}
          <Dropdown btnClass="outline-primary">
            <span slot="button" class="me-1"><Fa icon="{faPlus}" /> Add</span>
            <DropdownItem on:click="{addFolder}">Add Folder</DropdownItem>
            <DropdownItem on:click="{() => fileUploadElem.click()}">Upload File</DropdownItem>
          </Dropdown>
          <input type="file" style="display: none" bind:this="{fileUploadElem}" on:change="{uploadFile}" />
        {/if}

        {#if info?.mounts?.length > 0}
          <div class="ms-4">
            <Dropdown>
              <span slot="button" class="me-1"><Fa icon="{faHdd}" /> Volumes </span>
              {#each info.mounts as mount}
                <DropdownItem on:click="{() => loadPath(mount.destination)}">
                  <div class="d-flex justify-content-between align-items-center">
                    <span>{mount.destination}</span>
                    <span>
                      {#if mount.readonly}
                        <span class="badge bg-warning ms-2">readonly</span>
                      {/if}
                      <span class="badge bg-secondary ms-2">{mount.type}</span>
                    </span>
                  </div>
                </DropdownItem>
              {/each}
            </Dropdown>
          </div>
        {/if}
      </div>
    </div>

    <table class="table table-hover">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col" class="text-end">Size</th>
          <th scope="col" class="text-center">Owner</th>
          <th scope="col" class="text-center">Modified</th>
          <th scope="col" class="text-center">Permissions</th>
        </tr>
      </thead>
      <tbody>
        {#each currentEntries || [] as e}
          <tr class:clickable="{e.type === 'd' || allow_download}" on:click="{() => (e.type === 'd' ? gotoSubDir(e.name) : requestFileDownload(e.name))}">
            <td>
              {#if e.type === 'd'}
                <Fa icon="{faFolder}" size="lg" color="#3B6" />
              {:else if e.type === 'f'}
                <Fa icon="{faFile}" size="lg" color="#36B" />
              {:else if e.type === 'l'}
                <Fa icon="{faExternalLinkSquareAlt}" size="lg" color="#B36" />
              {:else}
                {e.type}
              {/if}
              <wbr />
              {e.name}
            </td>
            <td class="text-end" style="word-break: break-all">
              {#if e.type === 'f'}
                {e.filesize}
              {/if}
            </td>
            <td class="text-center">
              {e.owner}
              <wbr />{e.group}
            </td>
            <td class="text-center">
              {e.modtime}
            </td>
            <td class="text-center font-monospace" style="word-break: break-all">
              {e.permissions}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .clickable {
    cursor: pointer;
  }
</style>
