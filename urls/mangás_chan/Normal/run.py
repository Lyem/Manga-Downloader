import os
import re
import time
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, Style

import src.organizar as organizar
import src.move as move

async def run(driver, url, numero_capitulo, session, folder_selected, nome_foler, nome, debug_var, baixando_label, compactar, compact_extension, extension, download_folder, app_instance, max_attent, max_verify):
    folder_path = os.path.join(folder_selected, nome_foler, numero_capitulo)

    # Verificar se a pasta já existe e tem conteúdo
    contents = os.listdir(folder_path) if os.path.exists(folder_path) else []

    print(f"\n═══════════════════════════════════► {nome} -- {numero_capitulo} ◄═══════════════════════════════════════")

    if contents:
        print(f"{Fore.GREEN}INFO:{Style.RESET_ALL} a pasta {folder_path} já existe e contém arquivos. Excluindo conteúdo...")
        for item in contents:
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Exclui pasta e conteúdo
            else:
                os.remove(item_path)  # Exclui arquivo

    os.makedirs(folder_path, exist_ok=True)

    driver.get(url)
    
    if debug_var.get():
        baixando_label.config(text=f"Verificando capítulo {numero_capitulo}")
    
    # Injeta um script JavaScript para simular um pequeno movimento do mouse
    driver.execute_script("window.dispatchEvent(new Event('mousemove'));")

    time.sleep(1)
    
    # Simula a seleção da opção "Página Inteira" e aciona o evento de mudança
    driver.execute_script("var select = document.getElementById('readingmode');"
                            "select.value = 'full';"
                            "var event = new Event('change');"
                            "select.dispatchEvent(event);")

    time.sleep(1)

    def load_images():
        count_repet = 0
        count_save = 0
        paginas = [0]
        paginas_save = 0
        while count_repet < max_verify:
            try:
                if debug_var.get():
                    baixando_label.config(text=f"Carregando capítulo {numero_capitulo}\nVerificação {count_repet + 1} / {max_verify}\nEncontrados {len(paginas)} imagens")

                # Espera até que o elemento do leitor esteja presente na página
                leitor = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "readerarea"))
                )

                # Obtém todas as imagens dentro do leitor
                paginas = leitor.find_elements(By.TAG_NAME, 'img')

                # Função para rolar até a imagem e aguardar o carregamento
                def scroll_to_image(image_element):
                    driver.execute_script("arguments[0].scrollIntoView();", image_element)
                    wait_time = 0
                    while not image_element.get_attribute("complete") and wait_time < 10:
                        time.sleep(0.5)
                        wait_time += 1

                # Itera sobre as imagens
                for imagem in paginas:
                    scroll_to_image(imagem)

                count_repet += 1
            
                if len(paginas) != paginas_save:
                    paginas_save = len(paginas)
                    count_save += 1
                    
                else:
                    if count_save + 10 == count_repet:
                        break

            except Exception as e:
                print(f"Erro durante o carregamento de imagens: {e}")
                # Se ocorrer um erro, você pode querer tentar novamente ou lidar com a situação de outra maneira
    
    load_images()
    
    while True:
        # Espera até que o elemento do leitor esteja presente na página
        leitor = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "readerarea"))
        )

        # Obtém todas as imagens dentro do leitor
        paginas = leitor.find_elements(By.TAG_NAME, 'img')
        links_das_imagens = []

        # Função para rolar até a imagem e aguardar o carregamento
        def scroll_to_image(image_element):
            driver.execute_script("arguments[0].scrollIntoView();", image_element)
            wait_time = 0
            while not image_element.get_attribute("complete") and wait_time < 10:
                time.sleep(0.5)
                wait_time += 1

        # Itera sobre as imagens
        for imagem in paginas:
            scroll_to_image(imagem)
            
            # Aqui você pode adicionar o código para baixar a imagem ou qualquer outra ação desejada
            links_das_imagens.append(str(imagem.get_attribute('src')))
            
        # Extrai os links das imagens
        links_das_imagens = [link.strip() for link in links_das_imagens]
        links_count = str(len(links_das_imagens))
        
        if 'None' in links_das_imagens:
            load_images()
        else:
            break
    
    
    def download_images(count, files):
        for imagem in links_das_imagens:
            if debug_var.get():
                baixando_label.config(text=f"Capítulo {numero_capitulo}\nBaixando página: {count} / {links_count}")
                
            driver.get(imagem)
            
            try:
                input_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="number"]'))
                )
            except:
                driver.refresh()
                time.sleep(1)
                
                input_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="number"]'))
                )
            
            input_element.clear()  # Limpa qualquer valor existente no campo
            input_element.send_keys(count)
            
            download_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/button"))
            )
            download_button.click()
            
            extension_match = re.search(r'\.(jpg|jpeg|png|gif|bmp|webp)$', imagem, re.IGNORECASE)
            
            if extension_match:
                file_extension = extension_match.group(1)
            
            print(f"{Fore.GREEN}Baixando {imagem} como {count:02d}.{file_extension}...{Style.RESET_ALL}")
            
            time.sleep(0.2)
            
            attention = 0
            warning_img = 0
            while True:
                lista = os.listdir(download_folder)
                if len(lista) > files:
                    files += 1
                    break
                else:
                    if warning_img > max_attent:
                        print(f"{Fore.RED}Falha ao baixar {imagem} como {count:02d}.{file_extension}...{Style.RESET_ALL}")
                        break
                    elif attention < 1000:
                        attention += 1
                        time.sleep(0.1)
                        continue
                    else:
                        download_button.click()
                        attention = 0
                        warning_img += 1
                        continue
            
            count += 1
            
        return count
    
    download_images(1, 0)
    
    if debug_var.get():
        baixando_label.config(text=f"Arrumando páginas...")
    
    move.setup(download_folder, folder_path)
            
    organizar.organizar(folder_path, compactar, compact_extension, extension)

    if debug_var.get():
        baixando_label.config(text=f"Aguarde...")
        
    app_instance.move_text_wait(f'Capítulo {numero_capitulo} baixado com sucesso')

    print(f"═══════════════════════════════════► {nome} -- {numero_capitulo} ◄═══════════════════════════════════════\n")