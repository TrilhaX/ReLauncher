from __future__ import annotations

import json
import os
import sys
import threading
import time

import webview

from scripts.getInfoPlayer import getInfoPlayer
from scripts.functions import runClient, sendWebhook


CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "clients": [],
    "clientToPlayer": {},
    "clientToGame": {},
    "cdTime": 10,
    "webhookURL": None,
    "webhookEnabled": False,
}


def resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_config() -> dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        config = json.loads(json.dumps(DEFAULT_CONFIG))
        config.update(data)

        if not isinstance(config.get("clients"), list):
            config["clients"] = []
        if not isinstance(config.get("clientToPlayer"), dict):
            config["clientToPlayer"] = {}
        if not isinstance(config.get("clientToGame"), dict):
            config["clientToGame"] = {}

        return config
    except Exception:
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)

    temp_file = CONFIG_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)

    os.replace(temp_file, CONFIG_FILE)


class Monitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.last_status = {}
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            try:
                config = load_config()
                clients = list(config.get("clients", []))
                client_to_player = config.get("clientToPlayer", {})
                client_to_game = config.get("clientToGame", {})
                cd_time = max(1, int(config.get("cdTime", 10)))
                webhook_url = config.get("webhookURL")
                webhook_enabled = bool(config.get("webhookEnabled", False))

                self.last_status = {
                    name: status
                    for name, status in self.last_status.items()
                    if name in clients
                }

                for client in clients:
                    if not self.running:
                        break

                    player_id = client_to_player.get(client)
                    game_info = client_to_game.get(client, {})
                    place_id = game_info.get("placeID")
                    private_server_code = game_info.get("privateServerCode")

                    if not player_id or not place_id:
                        continue

                    try:
                        presence = getInfoPlayer(player_id)
                        status = presence.get("status", "Offline")
                        player_name = presence.get(
                            "name", f"Player {player_id}"
                        )
                    except Exception:
                        status = "Offline"
                        player_name = f"Player {player_id}"

                    previous = self.last_status.get(client)

                    if status != previous:
                        if (
                            status != "InGame"
                            and previous == "InGame"
                        ):
                            if webhook_enabled and webhook_url:
                                try:
                                    sendWebhook(
                                        webhook_url,
                                        f"'{player_name}' is now offline in '{client}'.",
                                    )
                                except Exception:
                                    pass

                        elif status == "InGame" and previous != "InGame":
                            if webhook_enabled and webhook_url:
                                try:
                                    sendWebhook(
                                        webhook_url,
                                        f"'{player_name}' is now InGame in '{client}'.",
                                    )
                                except Exception:
                                    pass

                    self.last_status[client] = status

                    print(
                        f"[DEBUG] {client} -> "
                        f"status={status} | "
                        f"last_status={self.last_status.get(client)}"
                    )

                    if status != "InGame":
                        try:
                            runClient(
                                client,
                                place_id,
                                private_server_code,
                            )
                            self.clients_status[client]["status"] = "online"
                        except Exception:
                            pass

                for _ in range(cd_time * 10):
                    if not self.running:
                        break
                    time.sleep(0.1)

            except Exception:
                time.sleep(2)


class Api:
    def __init__(self, window):
        self.window = window
        self.monitor = Monitor()

    def get_clients(self):
        config = load_config()
        result = []

        for client in config.get("clients", []):
            game = config.get("clientToGame", {}).get(client, {})
            raw_status = self.monitor.last_status.get(client, "Waiting")

            if raw_status == "InGame":
                status = "online"
            elif raw_status == "Online":
                status = "online"
            elif raw_status == "InStudio":
                status = "online"
            elif raw_status == "Offline":
                status = "offline"
            elif raw_status == "Invisible":
                status = "offline"
            else:
                status = "reconnecting"

            result.append(
                {
                    "name": client,
                    "playerId": str(
                        config.get("clientToPlayer", {}).get(client, "")
                    ),
                    "placeId": str(
                        game.get("placeID", "")
                    ),
                    "privateServerCode": str(
                        game.get("privateServerCode", "")
                    ),
                    "status": status,
                    "rawStatus": raw_status,
                }
            )

        return {
            "clients": result,
            "cdTime": config.get("cdTime", 10),
            "webhookEnabled": config.get("webhookEnabled", False),
            "webhookURL": config.get("webhookURL") or "",
            "monitoring": self.monitor.running,
        }

    def add_client(
        self,
        name,
        player_id,
        place_id,
        private_server_code="",
    ):
        name = str(name).strip()
        player_id = str(player_id).strip()
        place_id = str(place_id).strip()
        private_server_code = str(private_server_code or "").strip()

        if not name or not player_id or not place_id:
            return {"ok": False, "error": "Preencha nome, Player ID e Place ID."}

        config = load_config()

        if name in config["clients"]:
            return {"ok": False, "error": "Já existe um cliente com esse nome."}

        config["clients"].append(name)
        config["clientToPlayer"][name] = player_id
        config["clientToGame"][name] = {
            "placeID": place_id,
            "privateServerCode": private_server_code,
        }

        save_config(config)
        self.monitor.last_status[name] = "Waiting"

        return {"ok": True, "data": self.get_clients()}

    def edit_client(
        self,
        old_name,
        name,
        player_id,
        place_id,
        private_server_code="",
    ):
        old_name = str(old_name).strip()
        name = str(name).strip()
        player_id = str(player_id).strip()
        place_id = str(place_id).strip()
        private_server_code = str(private_server_code or "").strip()

        if not old_name or not name or not player_id or not place_id:
            return {"ok": False, "error": "Preencha todos os campos obrigatórios."}

        config = load_config()

        if old_name not in config["clients"]:
            return {"ok": False, "error": "Cliente não encontrado."}

        if name != old_name and name in config["clients"]:
            return {"ok": False, "error": "Já existe outro cliente com esse nome."}

        index = config["clients"].index(old_name)
        config["clients"][index] = name

        old_player = config["clientToPlayer"].pop(old_name, None)
        config["clientToPlayer"][name] = player_id or old_player

        old_game = config["clientToGame"].pop(old_name, {})
        config["clientToGame"][name] = {
            "placeID": place_id or old_game.get("placeID", ""),
            "privateServerCode": private_server_code,
        }

        if old_name != name:
            self.monitor.last_status.pop(old_name, None)

        save_config(config)
        return {"ok": True, "data": self.get_clients()}

    def remove_client(self, name):
        name = str(name).strip()
        config = load_config()

        if name not in config["clients"]:
            return {"ok": False, "error": "Cliente não encontrado."}

        config["clients"].remove(name)
        config["clientToPlayer"].pop(name, None)
        config["clientToGame"].pop(name, None)

        self.monitor.last_status.pop(name, None)
        save_config(config)

        return {"ok": True, "data": self.get_clients()}

    def save_settings(self, cd_time, webhook_enabled, webhook_url):
        try:
            cd_time = max(1, int(cd_time))
        except Exception:
            return {"ok": False, "error": "Intervalo inválido."}

        config = load_config()
        config["cdTime"] = cd_time
        config["webhookEnabled"] = bool(webhook_enabled)
        config["webhookURL"] = str(webhook_url or "").strip() or None
        save_config(config)

        return {"ok": True, "data": self.get_clients()}

    def start_monitor(self):
        self.monitor.start()
        return self.get_clients()

    def stop_monitor(self):
        self.monitor.stop()
        return self.get_clients()

    def close(self):
        self.monitor.stop()
        try:
            self.window.destroy()
        except Exception:
            pass


HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DumbKero</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 18px;
    background: #070b11;
    color: #e9eef7;
    font-family: Arial, sans-serif;
}
h1 { margin: 0; font-size: 23px; }
.subtitle { color: #7f8da3; font-size: 12px; margin-top: 5px; }
.top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}
button {
    border: 0;
    border-radius: 8px;
    padding: 9px 12px;
    cursor: pointer;
    color: white;
    background: #1c6ff2;
    font-weight: 600;
}
button:hover { filter: brightness(1.12); }
button.danger { background: #b83245; }
button.secondary { background: #202938; }
.card {
    background: #0d131d;
    border: 1px solid #1b2636;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
}
.card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.client {
    border: 1px solid #202d3f;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 9px;
    background: #0a1018;
}
.client:last-child { margin-bottom: 0; }
.client-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.client-name { font-weight: 700; }
.status {
    font-size: 11px;
    color: #8b9ab0;
    margin-top: 5px;
}
.actions { display: flex; gap: 6px; }
.actions button { padding: 7px 9px; font-size: 11px; }
.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 9px;
}
label {
    display: block;
    color: #9aa8bc;
    font-size: 11px;
    margin-bottom: 5px;
}
input {
    width: 100%;
    padding: 9px;
    border-radius: 8px;
    border: 1px solid #263448;
    background: #080d14;
    color: white;
    outline: none;
}
input:focus { border-color: #327ff5; }
.full { grid-column: 1 / -1; }
.form-actions {
    display: flex;
    gap: 7px;
    margin-top: 11px;
}
.hidden { display: none; }
.empty {
    color: #738198;
    text-align: center;
    padding: 15px;
    font-size: 12px;
}
.monitor {
    display: flex;
    align-items: center;
    gap: 9px;
}
.dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #667085;
}
.dot.on { background: #31c46c; box-shadow: 0 0 8px #31c46c; }
.small { font-size: 11px; color: #8190a6; }
.switch {
    display: flex;
    align-items: center;
    gap: 7px;
    margin-top: 10px;
    font-size: 12px;
}
.switch input { width: auto; }
</style>
</head>
<body>
<div class="top">
    <div>
        <h1>DumbKero</h1>
        <div class="subtitle">Client management and monitoring</div>
    </div>
    <div class="monitor">
        <span id="dot" class="dot"></span>
        <span id="monitorText" class="small">Stopped</span>
    </div>
</div>

<div class="card">
    <div class="card-title">
        <strong>Clients</strong>
        <button onclick="newClient()">+ Add Client</button>
    </div>
    <div id="clients"></div>
</div>

<div id="formCard" class="card hidden">
    <div class="card-title">
        <strong id="formTitle">Add Client</strong>
    </div>

    <div class="grid">
        <div class="full">
            <label>Client Name</label>
            <input id="name" placeholder="e.g., Client 1">
        </div>

        <div>
            <label>Player ID</label>
            <input id="playerId" placeholder="Roblox User ID">
        </div>

        <div>
            <label>Place ID</label>
            <input id="placeId" placeholder="Game ID">
        </div>

        <div class="full">
            <label>Private Server Code</label>
            <input id="privateServerCode" placeholder="Optional">
        </div>
    </div>

    <div class="form-actions">
        <button onclick="saveClient()">Save</button>
        <button class="secondary" onclick="cancelForm()">Cancel</button>
    </div>
</div>

<div class="card">
    <div class="card-title"><strong>Monitoring</strong></div>

    <div class="grid">
        <div>
            <label>Interval (seconds)</label>
            <input id="cdTime" type="number" min="1" value="10">
        </div>
        <div>
            <label>Webhook URL</label>
            <input id="webhookURL" placeholder="Optional">
        </div>
    </div>

    <div class="switch">
        <input id="webhookEnabled" type="checkbox">
        <span>Enable webhook</span>
    </div>

    <div class="form-actions">
        <button onclick="saveSettings()">Save Settings</button>
        <button id="monitorButton" class="secondary" onclick="toggleMonitor()">Start Monitoring</button>
    </div>
</div>

<script>
let editing = null;
let data = null;

function call(method, ...args) {
    return window.pywebview.api[method](...args);
}

async function refresh() {
    data = await call("get_clients");
    render();
}

function render() {
    const box = document.getElementById("clients");
    box.innerHTML = "";

    if (!data.clients.length) {
        box.innerHTML = '<div class="empty">Nenhum cliente cadastrado.</div>';
    } else {
        data.clients.forEach(c => {
            const div = document.createElement("div");
            div.className = "client";
            div.innerHTML = `
                <div class="client-head">
                    <div>
                        <div class="client-name">${esc(c.name)}</div>
                        <div class="status">
                            Player: ${esc(c.playerId)} · Place: ${esc(c.placeId)} · Status: ${esc(c.status)}
                        </div>
                    </div>
                    <div class="actions">
                        <button class="secondary" onclick='editClient(${JSON.stringify(c)})'>Editar</button>
                        <button class="danger" onclick='removeClient(${JSON.stringify(c.name)})'>Remover</button>
                    </div>
                </div>
            `;
            box.appendChild(div);
        });
    }

    document.getElementById("cdTime").value = data.cdTime;
    document.getElementById("webhookEnabled").checked = !!data.webhookEnabled;
    document.getElementById("webhookURL").value = data.webhookURL || "";

    document.getElementById("dot").className = data.monitoring ? "dot on" : "dot";
    document.getElementById("monitorText").textContent =
        data.monitoring ? "Monitorando" : "Parado";
    document.getElementById("monitorButton").textContent =
        data.monitoring ? "Parar monitoramento" : "Iniciar monitoramento";
}

function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, c => ({
        "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;"
    }[c]));
}

function newClient() {
    editing = null;
    document.getElementById("formTitle").textContent = "Adicionar cliente";
    document.getElementById("name").value = "";
    document.getElementById("playerId").value = "";
    document.getElementById("placeId").value = "";
    document.getElementById("privateServerCode").value = "";
    document.getElementById("formCard").classList.remove("hidden");
    document.getElementById("name").focus();
}

function editClient(c) {
    editing = c.name;
    document.getElementById("formTitle").textContent = "Editar cliente";
    document.getElementById("name").value = c.name;
    document.getElementById("playerId").value = c.playerId;
    document.getElementById("placeId").value = c.placeId;
    document.getElementById("privateServerCode").value = c.privateServerCode;
    document.getElementById("formCard").classList.remove("hidden");
}

async function saveClient() {
    const name = document.getElementById("name").value.trim();
    const playerId = document.getElementById("playerId").value.trim();
    const placeId = document.getElementById("placeId").value.trim();
    const privateServerCode = document.getElementById("privateServerCode").value.trim();

    const result = editing === null
        ? await call("add_client", name, playerId, placeId, privateServerCode)
        : await call("edit_client", editing, name, playerId, placeId, privateServerCode);

    if (!result.ok) {
        alert(result.error);
        return;
    }

    cancelForm();
    data = result.data;
    render();
}

async function removeClient(name) {
    if (!confirm(`Remover o cliente "${name}"?`)) return;

    const result = await call("remove_client", name);
    if (!result.ok) {
        alert(result.error);
        return;
    }

    data = result.data;
    render();
}

function cancelForm() {
    editing = null;
    document.getElementById("formCard").classList.add("hidden");
}

async function saveSettings() {
    const result = await call(
        "save_settings",
        document.getElementById("cdTime").value,
        document.getElementById("webhookEnabled").checked,
        document.getElementById("webhookURL").value
    );

    if (!result.ok) {
        alert(result.error);
        return;
    }

    data = result.data;
    render();
}

async function toggleMonitor() {
    data = data.monitoring
        ? await call("stop_monitor")
        : await call("start_monitor");

    render();
}

window.addEventListener("pywebviewready", refresh);
</script>
</body>
</html>
"""


def main():
    window = webview.create_window(
        "ReconnectX",
        html=HTML,
        width=520,
        height=820,
        min_size=(440, 650),
        background_color="#070b11",
    )

    api = Api(window)
    window.expose(
        api.get_clients,
        api.add_client,
        api.edit_client,
        api.remove_client,
        api.save_settings,
        api.start_monitor,
        api.stop_monitor,
        api.close,
    )

    webview.start()


if __name__ == "__main__":
    main()
