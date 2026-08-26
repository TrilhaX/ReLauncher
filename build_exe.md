# Gerando o ReconnectX.exe (arquivo único)

## 1. Rodar em desenvolvimento primeiro

Antes de empacotar, teste rodando direto com Python (mais rápido pra depurar):

```bash
pip install -r requirements.txt
python main.py
```

Isso deve abrir uma janela nativa com o dashboard. Verifique se:
- O indicador no topo direito muda para "Conectado" (bolinha verde) em alguns segundos.
- Se você já tem `Config/config.json` (gerado pelo `rejoinTool.py` original), os clientes
  aparecem na lista automaticamente.
- Se não tiver, vai aparecer um aviso em vermelho no log dizendo que falta configuração
  — isso é esperado por enquanto (a tela de "criar configuração" pela UI ainda não existe,
  ver seção "Próximos passos" no final).

## 2. Gerar o .exe (fazer no Windows, ou numa VM/CI Windows)

O PyInstaller empacota especificamente para o sistema operacional em que ele roda —
então para gerar um `.exe` Windows, o comando abaixo precisa rodar **no Windows**
(pode ser sua própria máquina, uma VM, ou um runner do GitHub Actions com `windows-latest`).

```powershell
pip install -r requirements.txt
pyinstaller --onefile --windowed --name ReconnectX --add-data "dashboard.html;." main.py
```

O executável final fica em `dist/ReconnectX.exe`. É esse arquivo que você entrega
para o cliente — um único `.exe`, sem precisar instalar Python.

### Parâmetros explicados
- `--onefile` → empacota tudo (Python + libs + dashboard.html) num único arquivo.
- `--windowed` → não abre o console preto do CMD junto com a janela do app.
- `--add-data "dashboard.html;."` → inclui o dashboard dentro do .exe (o `main.py`
  já sabe achar esse arquivo empacotado através da função `resource_path`).

### Se o cliente usa antivírus corporativo / SmartScreen
Executáveis feitos com PyInstaller às vezes disparam alerta de falso positivo em
antivírus (é comum, não é bug seu). Duas formas de reduzir isso:
- Assinar o `.exe` com um certificado de code signing (ideal a longo prazo).
- Adicionar um ícone customizado (`--icon=icone.ico`) — executáveis "genéricos"
  do PyInstaller tendem a ser mais sinalizados que os com metadata completa.

## 3. O que o cliente precisa ter instalado, além do .exe

- **ADB** (Android Debug Bridge) acessível no PATH, ou na mesma pasta do .exe —
  isso já era necessário no `rejoinTool.py` original, não mudou.
- Nada de Python, nada de pip. O `.exe` já leva tudo embutido.

## 4. Firewall

O app abre uma porta local (`127.0.0.1:8765`) só para a comunicação entre o
dashboard e o backend, dentro da própria máquina — nada é exposto para a rede.
Ainda assim, o Windows pode perguntar "permitir acesso na rede?" na primeira
execução; o cliente pode permitir (rede privada) sem risco, já que o servidor
só aceita conexões vindas do próprio computador.

---

## Próximos passos sugeridos (ainda não implementados)

1. **Tela de configuração inicial dentro do app** — hoje quem cria o
   `Config/config.json` ainda é o `rejoinTool.py` original (via terminal,
   perguntas de input). O ideal é ter uma tela "Adicionar cliente" no próprio
   dashboard, que escreve esse JSON, para o cliente final nunca precisar
   ver um terminal.
2. **Ícone e nome de app customizados** no instalador/exe.
3. **Auto-start com o Windows** (opcional), se o cliente quiser deixar
   monitorando sempre que ligar o PC.
