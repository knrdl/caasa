import { get, writable } from 'svelte/store'

const MSG_LIFETIME = 10 //secs

export const newQueueStore = function () {
    let store = writable<Message[]>([])

    setInterval(() => {
        let q = get(store)
        const now = Math.floor(new Date().getTime() / 1000)
        const filtered = q.filter(msg => msg.created_at + MSG_LIFETIME > now)
        if (filtered.length !== q.length)
            store.set(filtered)
    }, 1000)

    return {
        add(msg: Message) {
            let q = get(store)
            q.push({ ...msg, created_at: Math.floor(new Date().getTime() / 1000) })
            store.set(q)
        },
        remove(msg: Message) {
            let q = get(store)
            store.set(q.filter(m => !['created_at', 'type', 'text'].every(prop => m[prop] === msg[prop])))
        },
        subscribe: store.subscribe,
    }
}

export const messageBus = newQueueStore()

