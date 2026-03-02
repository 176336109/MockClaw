// Markdown-it configuration
const md = window.markdownit({
  html: true,
  linkify: true,
  breaks: true,
  highlight: function (str, lang) {
    if (lang && window.hljs) {
      if (window.hljs.getLanguage(lang)) {
        try {
          return window.hljs.highlight(str, { language: lang }).value
        } catch (__) {}
      } else {
        try {
          return window.hljs.highlightAuto(str).value
        } catch (__) {}
      }
    }
    return '' // use external default escaping
  }
})
.use(window.markdownitTaskLists)
.use(window.markdownitEmoji)

const $tree = document.getElementById('tree')
const $content = document.getElementById('content')
const $toc = document.getElementById('toc')
const $breadcrumb = document.getElementById('breadcrumb')
const $search = document.getElementById('search')
const $markmapSvg = document.getElementById('markmap')
const $toggleViewBtn = document.getElementById('toggle-view-btn')
const $viewContainer = document.getElementById('view-container')

let currentPath = ''
let currentMarkdown = ''
let isMarkmapMode = false
let markmapInstance = null

// --- Tree View ---

function buildTreeNode(node) {
  const container = document.createElement('div')
  
  if (node.type === 'dir') {
    const group = document.createElement('div')
    group.className = 'tree-group'
    
    // Directory Title
    const title = document.createElement('div')
    title.className = 'tree-item dir'
    title.innerHTML = `
      <span class="tree-arrow">▼</span>
      <i class="fa-regular fa-folder" style="color: #54aeff;"></i>
      <span>${node.name}</span>
    `
    title.onclick = (e) => {
      e.stopPropagation()
      title.classList.toggle('collapsed')
      const children = title.nextElementSibling
      if (children) {
        children.classList.toggle('hidden')
        // Update arrow
        const arrow = title.querySelector('.tree-arrow')
        arrow.textContent = children.classList.contains('hidden') ? '▶' : '▼'
      }
    }
    group.appendChild(title)
    
    // Children Container
    const children = document.createElement('div')
    children.className = 'tree-children'
    if (node.children) {
      for (const c of node.children) {
        children.appendChild(buildTreeNode(c))
      }
    }
    group.appendChild(children)
    container.appendChild(group)
    
  } else if (node.type === 'file') {
    const item = document.createElement('div')
    item.className = 'tree-item file'
    item.dataset.path = node.path
    item.innerHTML = `
      <i class="fa-regular fa-file" style="color: #8b949e;"></i>
      <span>${node.name}</span>
    `
    item.onclick = (e) => {
      e.stopPropagation()
      openFile(node.path)
    }
    container.appendChild(item)
  }
  return container
}

async function loadTree() {
  try {
    const res = await fetch('/api/tree')
    const tree = await res.json()
    $tree.innerHTML = ''
    $tree.appendChild(buildTreeNode(tree))
  } catch (e) {
    $tree.innerHTML = `<div style="padding:16px;color:red">Failed to load tree</div>`
  }
}

function activateTreeItem(p) {
  const items = $tree.querySelectorAll('.tree-item.file')
  items.forEach(i => i.classList.remove('active'))
  const el = Array.from(items).find(i => i.dataset.path === p)
  if (el) {
    el.classList.add('active')
    // Expand parents
    let parent = el.parentElement
    while (parent && parent !== $tree) {
      if (parent.classList.contains('tree-children')) {
        parent.classList.remove('hidden')
        const title = parent.previousElementSibling
        if (title) {
          title.classList.remove('collapsed')
          const arrow = title.querySelector('.tree-arrow')
          if(arrow) arrow.textContent = '▼'
        }
      }
      parent = parent.parentElement
    }
    el.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }
}

// --- Breadcrumb ---

function renderBreadcrumb(p) {
  const parts = p.split('/').filter(Boolean)
  const frag = document.createDocumentFragment()
  
  const home = document.createElement('span')
  home.innerHTML = '<i class="fa-solid fa-house"></i>'
  home.onclick = () => location.hash = ''
  frag.appendChild(home)
  
  let acc = []
  for (const part of parts) {
    const sep = document.createElement('span')
    sep.textContent = ' / '
    sep.style.margin = '0 6px'
    sep.style.cursor = 'default'
    frag.appendChild(sep)
    
    acc.push(part)
    const el = document.createElement('span')
    el.textContent = part
    const path = acc.join('/')
    el.onclick = () => openFile(path) // Re-open file or dir logic? For now assume file context mainly
    frag.appendChild(el)
  }
  $breadcrumb.innerHTML = ''
  $breadcrumb.appendChild(frag)
}

// --- TOC & Post Render ---

function slugify(s) {
  return s.toLowerCase().trim()
    .replace(/[^\w\u4e00-\u9fa5\- ]+/g, '')
    .replace(/\s+/g, '-')
}

function buildTOC() {
  const heads = $content.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const frag = document.createDocumentFragment()
  heads.forEach(h => {
    const id = slugify(h.textContent)
    h.id = h.id || id // Set id if missing
    
    const item = document.createElement('a')
    item.href = `#${h.id}`
    item.textContent = h.textContent
    item.title = h.textContent
    
    // Indent based on level
    const level = parseInt(h.tagName[1])
    item.style.paddingLeft = `${(level - 1) * 12}px`
    
    item.onclick = (e) => {
      e.preventDefault()
      h.scrollIntoView({ behavior: 'smooth' })
    }
    
    frag.appendChild(item)
  })
  $toc.innerHTML = ''
  $toc.appendChild(frag)
}

function postRender() {
  // Highlight.js is handled by markdown-it config
  
  // Mermaid
  const mermaidBlocks = $content.querySelectorAll('code.language-mermaid')
  mermaidBlocks.forEach(code => {
    const pre = code.parentElement
    const div = document.createElement('div')
    div.className = 'mermaid'
    div.textContent = code.textContent
    pre.replaceWith(div)
  })
  
  if (mermaidBlocks.length > 0 && window.mermaid) {
    window.mermaid.run().catch(err => console.error('Mermaid error:', err))
  }
  
  buildTOC()
}

// --- Markmap ---

function renderMarkmap() {
  if (!currentMarkdown) return
  
  if (markmapInstance) {
    markmapInstance.destroy()
    $markmapSvg.innerHTML = ''
  }
  
  const { Transformer } = window.markmap
  const { Markmap, loadCSS, loadJS } = window.markmap
  
  const transformer = new Transformer()
  const { root, features } = transformer.transform(currentMarkdown)
  
  if (features.styles) loadCSS(features.styles)
  if (features.scripts) loadJS(features.scripts, { getMarkmap: () => window.markmap })
  
  markmapInstance = Markmap.create($markmapSvg, null, root)
}

function toggleView() {
  isMarkmapMode = !isMarkmapMode
  
  if (isMarkmapMode) {
    $content.style.display = 'none'
    $markmapSvg.style.display = 'block'
    $toc.style.display = 'none'
    $toggleViewBtn.innerHTML = '<i class="fa-solid fa-file-lines"></i> 文档模式'
    renderMarkmap()
  } else {
    $content.style.display = 'block'
    $markmapSvg.style.display = 'none'
    $toc.style.display = 'block'
    $toggleViewBtn.innerHTML = '<i class="fa-solid fa-diagram-project"></i> 导图模式'
  }
}

$toggleViewBtn.onclick = toggleView

// --- Main Logic ---

async function openFile(p) {
  console.log('Opening file:', p)
  try {
    // Show loading state
    $content.innerHTML = '<div style="padding:20px;color:#8b949e">加载中...</div>'
    
    // Reset view to doc mode when opening new file
    if (isMarkmapMode) toggleView()
    
    const res = await fetch(`/api/file?path=${encodeURIComponent(p)}`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    
    const data = await res.json()
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    currentPath = data.path
    currentMarkdown = data.content
    renderBreadcrumb(currentPath)
    activateTreeItem(currentPath)
    
    // Render Markdown
    console.log('Rendering markdown...')
    $content.innerHTML = md.render(currentMarkdown)
    
    console.log('Post rendering...')
    postRender()
    console.log('File opened successfully')
    
  } catch (err) {
    console.error('Error opening file:', err)
    $content.innerHTML = `
      <div style="color:#f85149;padding:20px">
        <h3>无法打开文件</h3>
        <pre style="background:#161b22;padding:10px;border-radius:6px">${err.message}</pre>
        <p>请检查控制台获取更多详情。</p>
      </div>
    `
  }
}

function tryOpenFromHash() {
  const h = decodeURIComponent(location.hash || '').replace(/^#/, '')
  if (h.startsWith('p=')) {
    const p = h.slice(2)
    if (p) openFile(p)
  }
}

// Search
$search.addEventListener('input', () => {
  const kw = $search.value.trim().toLowerCase()
  const items = $tree.querySelectorAll('.tree-item.file')
  
  items.forEach(item => {
    const name = item.querySelector('span').textContent.toLowerCase()
    const match = name.includes(kw)
    
    // Toggle file visibility
    item.style.display = match ? 'flex' : 'none'
    
    // Handle parent groups visibility
    // If searching, expand all parents of matched items
    if (kw && match) {
      let parent = item.parentElement // .tree-group or root container
      while (parent && parent !== $tree) {
         if (parent.classList.contains('tree-children')) {
           parent.classList.remove('hidden')
           parent.parentElement.querySelector('.tree-item.dir').classList.remove('collapsed')
         }
         parent = parent.parentElement
      }
    }
  })
  
  // Hide empty directories if searching? (Optional enhancement)
})

window.addEventListener('hashchange', tryOpenFromHash)

// Init
async function main() {
  await loadTree()
  tryOpenFromHash()
}

main()
