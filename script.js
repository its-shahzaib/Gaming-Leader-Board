// static/script.js
const API = '/api'
const leaderboardEl = document.getElementById('leaderboard')
const top3Box = document.getElementById('top3Box')
const addForm = document.getElementById('addForm')
const playerName = document.getElementById('playerName')
const playerScore = document.getElementById('playerScore')
const simulateBtn = document.getElementById('simulateMatch')
const refreshBtn = document.getElementById('refresh')

async function fetchPlayers(){
  try{
    const res = await fetch(`${API}/players`)
    if(!res.ok) throw new Error('Failed to fetch')
    const data = await res.json()
    renderLeaderboard(data)
    renderTop3(data.slice(0,3))
  }catch(e){
    console.error(e)
  }
}

function renderTop3(topArr){
  top3Box.innerHTML = ''
  for(let i=0;i<3;i++){
    const p = topArr[i]
    const rank = i+1
    const div = document.createElement('div')
    div.className = 'top-card'
    if(p){
      div.innerHTML = `<div class="rank">#${rank}</div>
                       <div class="top-name">${p.name}</div>
                       <div class="top-score">${p.score}</div>`
    } else {
      div.innerHTML = `<div class="rank">#${rank}</div>
                       <div class="top-name">-</div>
                       <div class="top-score">0</div>`
    }
    top3Box.appendChild(div)
  }
}

function renderLeaderboard(arr){
  leaderboardEl.innerHTML = ''
  arr.forEach((p, idx) => {
    const row = document.createElement('div')
    row.className = 'row'
    row.innerHTML = `
      <div class="left">
        <div class="avatar">${p.name.slice(0,1).toUpperCase()}</div>
        <div>
          <div class="name">${p.name}</div>
          <div class="small">ID: ${p.id}</div>
        </div>
      </div>
      <div class="right" style="display:flex;align-items:center;gap:16px">
        <div class="score">${p.score}</div>
        <div class="actions">
          <button class="action-btn" onclick="showUpdate(${p.id}, ${p.score})">Update</button>
          <button class="action-btn danger" onclick="deletePlayer(${p.id})">Delete</button>
        </div>
      </div>
    `
    leaderboardEl.appendChild(row)
  })
}

addForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  const name = playerName.value.trim()
  const score = Number(playerScore.value)
  if(!name) return alert('Enter player name')
  await fetch(`${API}/players`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({name, score})
  })
  playerName.value = ''
  playerScore.value = 0
  await fetchPlayers()
})

window.showUpdate = async (id, currentScore) => {
  const input = prompt('Enter new score for player (ID '+id+'):', currentScore)
  if(input === null) return
  const val = Number(input)
  if(Number.isNaN(val)) return alert('Invalid number')
  await fetch(`${API}/players/${id}`, {
    method: 'PUT',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({score: val})
  })
  fetchPlayers()
}

window.deletePlayer = async (id) => {
  if(!confirm('Delete player ID '+id+'?')) return
  await fetch(`${API}/players/${id}`, {method:'DELETE'})
  fetchPlayers()
}

simulateBtn.addEventListener('click', async () => {
  // Simulate random match: pick a random player and add random score
  try{
    const res = await fetch(`${API}/players`)
    const arr = await res.json()
    if(arr.length === 0) return alert('No players to simulate')
    const rand = arr[Math.floor(Math.random()*arr.length)]
    const add = Math.floor(Math.random()*400) + 10
    const newScore = rand.score + add
    await fetch(`${API}/players/${rand.id}`, {
      method:'PUT',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({score: newScore})
    })
    // small celebratory flash on page
    const old = document.body.style.background
    document.body.style.transition = 'background .2s'
    document.body.style.background = 'linear-gradient(180deg,#0b2a1f,#07221a)'
    setTimeout(()=> document.body.style.background = old, 350)
    fetchPlayers()
  }catch(e){ console.error(e) }
})

refreshBtn.addEventListener('click', fetchPlayers)

// initial fetch + periodic refreshing (dynamic)
fetchPlayers()
setInterval(fetchPlayers, 2500)  // every 2.5s refresh to show dynamic updates