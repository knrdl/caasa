import App from './App.svelte'
import 'bootstrap-dark-5/dist/css/bootstrap-nightshade.min.css'
import './app.css'
import { mount } from 'svelte'

const app = mount(App, { target: document.getElementById("app")! })

export default app
