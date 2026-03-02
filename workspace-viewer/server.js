const http = require('http')
const fs = require('fs')
const path = require('path')
const { URL } = require('url')

const cwd = __dirname
const configPath = path.join(cwd, 'openclaw-viewer.config.json')
let config = {}
try {
  const raw = fs.readFileSync(configPath, 'utf-8')
  config = JSON.parse(raw)
} catch (e) {
  config = {}
}
const defaultRoot = path.join(process.env.HOME || '', '.openclaw', 'workspace')
const ROOT = path.resolve(config.root || defaultRoot)
const PORT = Number(process.env.PORT || config.port || 4310)
const STATIC_DIR = path.join(cwd, 'web')
const IGNORE = new Set(['node_modules', '.git', '.DS_Store'])
const ALLOWED_EXT = new Set(['.md', '.mdx'])

function isUnderRoot(abs) {
  const rel = path.relative(ROOT, abs)
  return !!rel && !rel.startsWith('..') && !path.isAbsolute(rel)
}

function toRelPosix(abs) {
  const rel = path.relative(ROOT, abs)
  return rel.split(path.sep).join('/')
}

function readDirTree(dir) {
  let entries = []
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true })
  } catch (e) {
    return null
  }
  const dirs = []
  const files = []
  for (const ent of entries) {
    if (IGNORE.has(ent.name) || ent.name.startsWith('.')) continue
    const abs = path.join(dir, ent.name)
    if (ent.isDirectory()) {
      const child = readDirTree(abs)
      if (!child) continue
      dirs.push({
        type: 'dir',
        name: ent.name,
        path: toRelPosix(abs),
        children: child.children
      })
    } else if (ent.isFile()) {
      const ext = path.extname(ent.name).toLowerCase()
      if (ALLOWED_EXT.has(ext)) {
        files.push({
          type: 'file',
          name: ent.name,
          path: toRelPosix(abs)
        })
      }
    }
  }
  dirs.sort((a, b) => a.name.localeCompare(b.name))
  files.sort((a, b) => a.name.localeCompare(b.name))
  return { type: 'dir', name: path.basename(dir), path: toRelPosix(dir) || '', children: [...dirs, ...files] }
}

function sendJson(res, obj, code = 200) {
  const body = JSON.stringify(obj)
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-cache'
  })
  res.end(body)
}

function getMime(p) {
  const ext = path.extname(p).toLowerCase()
  if (ext === '.html') return 'text/html; charset=utf-8'
  if (ext === '.js') return 'application/javascript; charset=utf-8'
  if (ext === '.css') return 'text/css; charset=utf-8'
  if (ext === '.svg') return 'image/svg+xml'
  if (ext === '.json') return 'application/json; charset=utf-8'
  if (ext === '.png') return 'image/png'
  if (ext === '.jpg' || ext === '.jpeg') return 'image/jpeg'
  return 'application/octet-stream'
}

const server = http.createServer((req, res) => {
  const u = new URL(req.url, `http://${req.headers.host}`)
  console.log(`${new Date().toISOString()} ${req.method} ${u.pathname}${u.search}`)
  const pathname = decodeURIComponent(u.pathname)
  if (pathname === '/api/tree') {
    const tree = readDirTree(ROOT) || { type: 'dir', name: path.basename(ROOT), path: '', children: [] }
    return sendJson(res, tree)
  }
  if (pathname === '/api/file') {
    const rel = u.searchParams.get('path') || ''
    if (!rel) return sendJson(res, { error: 'missing path' }, 400)
    const cleaned = rel.replace(/^\/+/, '')
    const abs = path.resolve(ROOT, cleaned)
    if (!isUnderRoot(abs)) return sendJson(res, { error: 'forbidden' }, 403)
    const ext = path.extname(abs).toLowerCase()
    if (!ALLOWED_EXT.has(ext)) return sendJson(res, { error: 'unsupported file type' }, 400)
    let stat
    try {
      stat = fs.statSync(abs)
      if (!stat.isFile()) throw new Error('not a file')
    } catch (e) {
      return sendJson(res, { error: 'not found' }, 404)
    }
    const size = stat.size
    if (size > (config.maxFileSize || 5 * 1024 * 1024)) return sendJson(res, { error: 'file too large' }, 413)
    let content = ''
    try {
      content = fs.readFileSync(abs, 'utf-8')
    } catch (e) {
      return sendJson(res, { error: 'read error' }, 500)
    }
    return sendJson(res, { path: toRelPosix(abs), mtime: stat.mtimeMs, size, content })
  }
  let filePath = STATIC_DIR
  if (pathname === '/' || pathname === '') {
    filePath = path.join(STATIC_DIR, 'index.html')
  } else {
    filePath = path.join(STATIC_DIR, pathname.replace(/^\/+/, ''))
  }
  if (!filePath.startsWith(STATIC_DIR)) {
    res.writeHead(403)
    return res.end('forbidden')
  }
  fs.readFile(filePath, (err, data) => {
    if (err) {
      const fallback = path.join(STATIC_DIR, 'index.html')
      fs.readFile(fallback, (e2, d2) => {
        if (e2) {
          res.writeHead(404)
          res.end('not found')
        } else {
          res.writeHead(200, { 'Content-Type': getMime(fallback) })
          res.end(d2)
        }
      })
    } else {
      res.writeHead(200, { 'Content-Type': getMime(filePath) })
      res.end(data)
    }
  })
})

server.listen(PORT, () => {
  console.log(`OpenClaw Workspace Viewer: http://localhost:${PORT}/`)
  console.log(`Root: ${ROOT}`)
})

