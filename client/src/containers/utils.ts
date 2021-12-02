export function round(value: number, postDecimal: number = 0) {
    return Math.round(value * 10 ** postDecimal) / 10 ** postDecimal
}

export function bytes2human(value: number) {
    const prefixes = ['', 'Ki', 'Mi', 'Gi', 'Ti']
    let prefixCtr = 0
    while (value >= 1024) {
        value /= 1024
        prefixCtr++
    }
    const preDecimal = Math.max(Math.floor(Math.log10(Math.floor(value))), 0)
    return round(value, 2 - preDecimal) + ' ' + prefixes[prefixCtr] + 'B'
}

export function fmtDate(date: string) {
    const d = new Date(date)
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`
}

export function downloadBlob(blob: Blob, filename: string) {
    // @ts-ignore
    if (window?.navigator?.msSaveOrOpenBlob) {
        // @ts-ignore
        window.navigator.msSaveOrOpenBlob(blob, filename)
    } else {
        const a = document.createElement('a')
        document.body.appendChild(a)
        const url = window.URL.createObjectURL(blob)
        a.href = url
        a.download = filename
        a.click()
        setTimeout(() => {
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
        }, 0)
    }
}
