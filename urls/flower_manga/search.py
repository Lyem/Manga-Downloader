import os
import re
import sys
import time
import shutil
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from colorama import Fore, Style

def obter_capitulos(driver, url, inicio, fim, debug_var, baixando_label):
    # Abre a página
    driver.get(url)
    
    # Aguarde um pouco para garantir que a página seja totalmente carregada (você pode ajustar esse tempo conforme necessário)
    driver.implicitly_wait(5)
    
    # Verifica se a página contém o texto "Página não encontrada"
    if "Página não encontrada" in driver.page_source:
            print("Erro: URL inválida. Status code: 404")
            driver.quit()
            return 'e1'
    
    time.sleep(5)
    
    os.system("cls")
    print("Verificando capítulos...")
    if debug_var.get():
        baixando_label.config(text="Verificando capítulos...")

    capitulos_encontrados = []
    
    # Executar o script JavaScript
    script = """
    var botao = document.querySelector('.c-chapter-readmore .btn');
    if (botao) {
        botao.click();
    } else {
        console.error("O botão não foi encontrado.");
    }
    """

    # Executar o script usando execute_script
    try:
        driver.execute_script(script)
    except Exception:
        pass

    time.sleep(2)

    # Localiza os elementos que contêm as informações dos capítulos
    chapter_elements = driver.find_elements(By.CLASS_NAME, "wp-manga-chapter")

    capitulos_encontrados = []

    for capitulo in chapter_elements:
        # Encontra o elemento 'a' dentro do 'li'
        a_element = capitulo.find_element(By.TAG_NAME, "a")

        # Obtém o texto do número do capítulo
        # Usa expressão regular para extrair números, pontos e vírgulas
        numero_capitulo = float(re.sub(r'[^0-9.,]', '', a_element.text.replace(',', '')))
        link = a_element.get_attribute("href")

        if inicio <= numero_capitulo <= fim:
            capitulos_encontrados.append({'numero_capitulo': numero_capitulo, 'link': link})
        
    return capitulos_encontrados
