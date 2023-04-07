// в описании путей слеши стилизованы отдельно
function replace_path(paths, paths_data) {
    var re = new RegExp('^{.*}$')
    for (let i = 0; i < paths.length; i++) {
        // console.log(paths_data[i].dataset.path)
        pathParts = paths_data[i].dataset.path.split('/')
        let content = ''
        pathParts.forEach((val, key) => {
            if (val) {
                if (re.test(val)) {
                    val=val.slice(1,-1)
                    content += `<span class="summary-path slash">/</span><span class="brace">{</span><span class="summary-path param">${val}</span><span class="brace">}</span>`
                } else {
                    content += `<span class="summary-path slash">/</span><span>${val}</span>`
                }
            }
        })
        paths[i].innerHTML = content
    }
}

window.onload = function () {

    (async () => {
        // console.log('path')
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

