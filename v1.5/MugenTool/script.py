import os
import requests
import zipfile
import subprocess

CURRENT_EXE_NAME = 'MugenTool.exe'
CURRENT_EXE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), CURRENT_EXE_NAME)
TEMP_ZIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_atualizacao.zip')

def get_current_version():
    return "1.5"  # Versão atual sem o prefixo 'v'

def get_latest_version():
    try:
        response = requests.get('https://api.github.com/repos/TrilhaX/ReLauncher/releases/latest')
        if response.status_code == 200:
            return response.json()['tag_name'].lstrip('v')  # Remove 'v' do início
        else:
            print("Erro ao obter a versão mais recente:", response.status_code)
            return None
    except Exception as e:
        print("Ocorreu um erro:", e)
        return None

def download_update():
    print("Baixando atualização...")
    try:
        response = requests.get('https://api.github.com/repos/TrilhaX/ReLauncher/releases/latest')
        if response.status_code == 200:
            assets = response.json().get('assets', [])
            for asset in assets:
                if asset['name'] == 'MugenTool.zip':
                    download_url = asset['url']
                    zip_response = requests.get(download_url, headers={'Accept': 'application/octet-stream'})
                    if zip_response.status_code == 200:
                        with open(TEMP_ZIP_PATH, 'wb') as file:
                            file.write(zip_response.content)
                        print("Atualização baixada com sucesso.")
                        return True
                    else:
                        print("Erro ao baixar o arquivo ZIP:", zip_response.status_code)
                        return False
    except Exception as e:
        print("Ocorreu um erro ao tentar baixar a atualização:", e)
    return False

def extract_update():
    if not os.path.exists(TEMP_ZIP_PATH):
        print(f"Arquivo não encontrado: {TEMP_ZIP_PATH}")
        return
    print("Extraindo atualização...")
    with zipfile.ZipFile(TEMP_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extract(CURRENT_EXE_NAME, os.path.dirname(os.path.abspath(__file__)))
    print("Atualização extraída com sucesso.")

def install_update():
    print("Instalando atualização...")
    os.replace(TEMP_ZIP_PATH, CURRENT_EXE_PATH)
    print("Atualização instalada com sucesso.")

def clear_cmd():
    # Limpa a tela do CMD
    subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)

def main():
    current_version = get_current_version()
    latest_version = get_latest_version()
    
    if latest_version and current_version != latest_version:
        clear_cmd()  # Limpa o CMD antes de fazer as perguntas
        user_input = input("Você deseja instalar a atualização? (s/n): ").strip().lower()
        if user_input == 's':
            if download_update():
                extract_update()
                install_update()
                print("Atualização concluída.")
            else:
                print("Erro ao baixar a atualização.")
        else:
            print("Atualização não instalada.")
    else:
        print("Você já está usando a versão mais recente.")

if __name__ == "__main__":
    main()
