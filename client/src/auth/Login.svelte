<script lang="ts">
  import Message from '../messages/Message.svelte'
  import api from '../api'
  import { slide } from 'svelte/transition'
  import LoadingScreen from '../LoadingScreen.svelte'
  import { createEventDispatcher, onDestroy, onMount } from 'svelte'
  import { messageBus } from '../messages/message-store'

  export let username: string = '' // on modify: update reference in .github/workflows/github-page.yml
  let password: string = '' // on modify: update reference in .github/workflows/github-page.yml
  let loading: boolean = false
  let errMsg = ''

  const dispatch = createEventDispatcher()

  onMount(() => {
    api.register<{ username: string }>(
      'login',
      ({ username }) => {
        dispatch('login', { username })
      },
      (err) => {
        loading = false
        messageBus.add({ text: err, type: 'error' })
      }
    )
  })

  onDestroy(() => {
    api.unregister('login')
  })

  async function login() {
    loading = true
    api.send('login', { username, password })
    errMsg = ''
    password = ''
  }
</script>

{#if loading}
  <LoadingScreen />
{/if}
<div class="container pt-5">
  {#if errMsg}
    <Message type="error" dismissible="{true}">{errMsg}</Message>
  {/if}
  <form class="container login-form" on:submit|preventDefault="{() => login()}" transition:slide|local>
    <div class="form-floating mb-2">
      <input
        type="text"
        class="form-control"
        id="loginName"
        placeholder=" "
        bind:value="{username}"
        on:input="{() => {
          username = username.toLowerCase().trim()
        }}"
        required
        autocomplete="username"
      />
      <label for="loginName">Username</label>
    </div>
    <div class="form-floating mb-2">
      <input type="password" class="form-control" id="loginPw" placeholder=" " bind:value="{password}" required autocomplete="current-password" />
      <label for="loginPw">Password</label>
    </div>
    <div class="col-12">
      <button type="submit" class="btn btn-primary w-100">Login</button>
    </div>
  </form>
</div>

<style>
  .login-form {
    max-width: 350px;
  }
</style>
