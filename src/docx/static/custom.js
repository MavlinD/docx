// в оиписании путей слеши стилизованы отдельно
function replace_path(paths, paths_data) {
    for (let i = 0; i < paths.length; i++) {
        paths[i].innerHTML = paths_data[i].dataset.path.split('/').join('<span class="summary-path slash">/</span>')
    }
}

window.onload = function () {

    (async () => {
        let paths
        let paths_data
        for (let i = 0; i < 10; i++) {
            paths_data = document.querySelectorAll('.opblock-summary-path')
            paths = document.querySelectorAll('.opblock-summary-path a span')
            if (!paths.length) {
                await sleep(500)
            } else {
                replace_path(paths, paths_data)
                return
            }
        }
        // console.log(paths)
    })()
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))

