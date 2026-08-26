from __future__ import annotations

import asyncio
import json
import threading
import time

import websockets

from scripts.functions import runClient, sendWebhook
from scripts.getInfoPlayer import getInfoPlayer
from scripts.manageFiles import loadConfig, checkIfAlrSaved
from scripts.createFiles import checkConfigFolder


DEFAULT_CONFIG_PATH = "Config/config.json"


class WSServer:
    """Servidor WebSocket assíncrono: transmite estado/log ao dashboard e
    encaminha comandos recebidos dele para o Monitor."""

    def __init__(self, host: str, port: int, loop: asyncio.AbstractEventLoop):
        self.host = host
        self.port = port
        self.loop = loop
        self.clients: set = set()
        self.commands_handler = None

    async def start(self):
        await websockets.serve(self._handle_client, self.host, self.port)

    async def _handle_client(self, ws):
        self.clients.add(ws)
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if self.commands_handler:
                    self.commands_handler(msg)
        finally:
            self.clients.discard(ws)

    def broadcast(self, message: dict):
        """Thread-safe: pode ser chamado de QUALQUER thread (ex: a thread do monitor)."""
        if not self.clients:
            return
        payload = json.dumps(message)
        asyncio.run_coroutine_threadsafe(self._broadcast_async(payload), self.loop)

    async def _broadcast_async(self, payload: str):
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send(payload)
            except websockets.exceptions.ConnectionClosed:
                dead.append(ws)
        for ws in dead:
            self.clients.discard(ws)


class Monitor:
    """Encapsula o loop original do rejoinTool, empurrando estado em vez de imprimir."""

    def __init__(self, broadcaster: WSServer):
        self.broadcaster = broadcaster
        self.mode = "stopped" 
        self.config: dict = {}
        self.clients_status: dict[str, dict] = {}
        self.rejoins_total = 0
        self._lock = threading.Lock()

    def handle_command(self, msg: dict):
        cmd = msg.get("type")
        with self._lock:
            if cmd == "toggle_auto":
                self.mode = "running" if self.mode in ("stopped", "paused") else "paused"
            elif cmd == "toggle_pause":
                if self.mode != "stopped":
                    self.mode = "paused" if self.mode == "running" else "running"
            elif cmd == "stop":
                self.mode = "stopped"

        if cmd == "stop":
            self.log("ERR", "Monitoramento parado pelo usuário.")
        self.push_state()

    def log(self, tag: str, text: str):
        self.broadcaster.broadcast({"type": "log", "tag": tag, "text": text})

    def push_state(self):
        clients_payload = [{"name": name, **data} for name, data in self.clients_status.items()]
        self.broadcaster.broadcast({
            "type": "state",
            "mode": self.mode,
            "rejoins_total": self.rejoins_total,
            "pkgs": len(self.config.get("clients", [])),
            "clients": clients_payload,
        })

    def run_forever(self):
        checkConfigFolder()
        if checkIfAlrSaved():
            self.config = loadConfig(DEFAULT_CONFIG_PATH) or {}
        else:
            self.config = {}
            self.log(
                "ERR",
                "Nenhuma configuração encontrada em Config/config.json. "
                "Gere uma configuração antes de iniciar (a tela de setup no app ainda é o próximo passo).",
            )

        clients = self.config.get("clients", [])
        clientToPlayer = self.config.get("clientToPlayer", {})
        clientToGame = self.config.get("clientToGame", {})
        cdTime = self.config.get("cdTime", 10)
        webhookURL = self.config.get("webhookURL")
        webhookEnabled = self.config.get("webhookEnabled", False)

        for c in clients:
            self.clients_status[c] = {"status": "offline", "rejoins": 0}

        with self._lock:
            self.mode = "running" if clients else "stopped"
        self.push_state()

        last_status = {c: None for c in clients}

        while True:
            if self.mode in ("stopped", "paused"):
                time.sleep(0.5)
                continue

            if not clients:
                time.sleep(1)
                continue

            for client in clients:
                if self.mode in ("stopped", "paused"):
                    break

                player_id = clientToPlayer.get(client)
                gameInfo = clientToGame.get(client, {})
                place_id = gameInfo.get("placeID")
                privateServerCode = gameInfo.get("privateServerCode")

                if not player_id or not place_id:
                    self.log("ERR", f"Configuração incompleta para '{client}'. Pulando...")
                    continue

                presence = getInfoPlayer(player_id)
                status = presence.get("status", "Offline")
                player_name = presence.get("name", f"Player {player_id}")
                prev = last_status.get(client)

                self.clients_status[client] = {
                    "status": "InGame" if status == "InGame" else "offline",
                    "rejoins": self.clients_status.get(client, {}).get("rejoins", 0),
                }

                if status != prev:
                    if status != "InGame" and prev == "InGame":
                        self.log("ERR", f"'{player_name}' saiu do jogo em '{client}'.")
                        if webhookEnabled and webhookURL:
                            sendWebhook(webhookURL, f"'{player_name}' saiu do jogo em '{client}'.")
                    elif status == "InGame" and prev != "InGame":
                        self.log("OK", f"'{player_name}' está em jogo em '{client}'.")
                        if webhookEnabled and webhookURL:
                            sendWebhook(webhookURL, f"'{player_name}' entrou em '{client}'.")
                last_status[client] = status

                if status != "InGame":
                    self.log("HOP", f"'{client}' — fora do jogo, reconectando...")
                    self.clients_status[client]["status"] = "reconnecting"
                    self.push_state()
                    try:
                        runClient(client, place_id, privateServerCode)
                        self.clients_status[client]["rejoins"] += 1
                        self.rejoins_total += 1
                        self.log("OK", f"'{client}' — cliente reaberto com sucesso.")
                    except Exception as e:
                        self.log("ERR", f"Falha ao reabrir '{client}': {e}")
                else:
                    self.log("WAIT", f"'{client}' — em jogo, nada a fazer.")

                self.push_state()

            time.sleep(cdTime)
