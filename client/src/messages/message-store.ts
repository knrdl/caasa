import { get, writable } from 'svelte/store'

const MSG_LIFETIME = 10 //secs

export const newQueueStore = function () {
    let store = writable<Message[]>([])

    setInterval(() => {
        let q = get(store)
        const now = Math.floor(new Date().getTime() / 1000)
        const filtered = q.filter(msg => msg.created_at! + MSG_LIFETIME > now)
        if (filtered.length !== q.length)
            store.set(filtered)
    }, 1000)

    return {
        add(msg: Message) {
            store.update(updater => ([...updater, { ...msg, created_at: Math.floor(new Date().getTime() / 1000) }]))
        },
        remove(msg: Message) {
            store.update(updater => updater.filter(m => m.created_at !== msg.created_at || m.type !== msg.type || m.text !== msg.text))
        },
        subscribe: store.subscribe,
    }
}

export const messageBus = newQueueStore()

