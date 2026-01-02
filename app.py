# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import heapq
import threading

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)

# -------------------------
# Data structures (DSA part)
# -------------------------

class Player:
    def __init__(self, pid: int, name: str, score: int):
        self.id = pid
        self.name = name
        self.score = int(score)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "score": self.score}


class PlayerNode:
    def __init__(self, player: Player):
        self.player = player
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self._lock = threading.Lock()

    def append(self, player: Player):
        with self._lock:
            node = PlayerNode(player)
            if not self.head:
                self.head = node
                return
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node

    def find_by_id(self, pid: int):
        cur = self.head
        while cur:
            if cur.player.id == pid:
                return cur
            cur = cur.next
        return None

    def delete_by_id(self, pid: int) -> bool:
        with self._lock:
            cur = self.head
            prev = None
            while cur:
                if cur.player.id == pid:
                    if prev:
                        prev.next = cur.next
                    else:
                        self.head = cur.next
                    return True
                prev = cur
                cur = cur.next
            return False

    def to_list(self):
        arr = []
        cur = self.head
        while cur:
            arr.append(cur.player.to_dict())
            cur = cur.next
        return arr

    def update_score(self, pid: int, new_score: int) -> bool:
        node = self.find_by_id(pid)
        if node:
            node.player.score = int(new_score)
            return True
        return False

    def clear(self):
        with self._lock:
            self.head = None

# -------------------------
# Sorting & heap helpers
# -------------------------

def quick_sort(arr, key='score'):
    # Quick sort that sorts list of dicts descending by 'score'
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2][key]
    left = [x for x in arr if x[key] > pivot]
    middle = [x for x in arr if x[key] == pivot]
    right = [x for x in arr if x[key] < pivot]
    return quick_sort(left, key) + middle + quick_sort(right, key)

def get_top_k_using_heap(arr, k=3):
    # Use a max-heap (by inverting score into negative for heapq)
    if not arr:
        return []
    # For efficiency, use nlargest
    topk = heapq.nlargest(k, arr, key=lambda x: x['score'])
    return topk

# -------------------------
# In-memory storage & ID management
# -------------------------
players = LinkedList()
_next_id = 1
_id_lock = threading.Lock()

def get_next_id():
    global _next_id
    with _id_lock:
        nid = _next_id
        _next_id += 1
    return nid

# insert some demo players for nice initial UI
demo_players = [
    ("ShadowRogue", 1200),
    ("PixelMage", 980),
    ("ZenArcher", 1100),
    ("NeonNinja", 1340),
    ("LunaBlade", 870),
]
for name, score in demo_players:
    players.append(Player(get_next_id(), name, score))

# -------------------------
# Routes
# -------------------------

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/players', methods=['GET'])
def api_get_players():
    arr = players.to_list()
    sorted_arr = quick_sort(arr, key='score')  # descending
    return jsonify(sorted_arr), 200

@app.route('/api/top3', methods=['GET'])
def api_get_top3():
    arr = players.to_list()
    top3 = get_top_k_using_heap(arr, 3)
    # ensure sorted descending
    top3_sorted = quick_sort(top3, key='score')
    return jsonify(top3_sorted), 200

@app.route('/api/players', methods=['POST'])
def api_add_player():
    data = request.json or {}
    name = data.get('name')
    score = int(data.get('score', 0))
    if not name:
        return jsonify({"error": "name required"}), 400
    new_player = Player(get_next_id(), name, score)
    players.append(new_player)
    return jsonify(new_player.to_dict()), 201

@app.route('/api/players/<int:pid>', methods=['PUT'])
def api_update_player(pid):
    data = request.json or {}
    new_score = data.get('score')
    if new_score is None:
        return jsonify({"error": "score required"}), 400
    ok = players.update_score(pid, int(new_score))
    if not ok:
        return jsonify({"error": "player not found"}), 404
    return jsonify({"status": "updated"}), 200

@app.route('/api/players/<int:pid>', methods=['DELETE'])
def api_delete_player(pid):
    ok = players.delete_by_id(pid)
    if not ok:
        return jsonify({"error": "player not found"}), 404
    return jsonify({"status": "deleted"}), 200

# -------------------------
# Run
# -------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)