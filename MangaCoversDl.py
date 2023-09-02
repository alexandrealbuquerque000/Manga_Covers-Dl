import os
from pathlib import Path
import time
import requests
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup # Para manipular e guardar dados obtidos do site
from tkinter import Tk, filedialog

 # Função para verificar existência de pasta ou arquivo
def verifpath(dirp, mode):

    if (os.path.exists(dirp))==True:
        if mode==0:

            return True
    else:
        if mode==0:

            return False
        else:
            os.mkdir(dirp)
        
    return dirp


# Função para obter o diretório central de destino dos arquivos
def gethqpath():

    root = Tk()
    root.geometry('0x0')
    hqpathchoose=('Selecione o diretório da pasta que deseja guardar todos os conteúdos escolhidos: ')
    hqpathstr=hqpathchoose.replace('Selecione', '\nDigite')
    print('\n'+hqpathchoose)
    hqpath = filedialog.askdirectory(parent=root, initialdir="/",title=hqpathchoose)
    root.destroy()       

    if hqpath=='':
        print('\nOpção cancelada.\n\nTente novamente')
        hqpath=input(hqpathstr)
    while ((Path(hqpath)).is_dir())==False:
        print("\nEsse diretório não existe.\n\nTente novamente.")
        hqpath=input(hqpathstr)
    
    return hqpath


# Função para obter informações de todas as requisições feitas pelo programa
def getinfo(site, mode=0, classinfo=0, extrainfo=0, getname=None, geturl=None):


    def by_webdriver(site):

        options = EdgeOptions()
        options.headless = True
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = Edge(service=Service(EdgeChromiumDriverManager(log_level=0, print_first_line=False).install()), options = options)
        driver.get(site)
        time.sleep(5)

        return driver
    

    # Função para definir o tipo de informação que será extraída da URL
    def get(infofilter):
        nonlocal info

        if infofilter=='text':
            exactinfo=info.get_text()
        else:
            exactinfo=info.get(infofilter)
        if exactinfo==None:
            exactinfo=''

        return exactinfo.strip()


    headers={'User-agent': 'Mozilla/5.0'}

    try:
        response = requests.get(site, stream=True, headers=headers)
        page_text=by_webdriver(site).page_source

    except requests.RequestException as error: 
        print('\nOcorreu um erro: '+ str(error))
        time.sleep(1.25)

        return -10
    if response.status_code==200:
        if mode:
        
            return response
        soup = BeautifulSoup(page_text, 'html.parser')
        if classinfo!=0 and extrainfo!=0:
            allinfo=soup.find_all(extrainfo, class_=classinfo)
        else:
            if classinfo!=0:
                allinfo=soup.find_all(class_=classinfo)
            else:
                allinfo=soup.find_all(extrainfo)
      
        listinfo=[]
        for info in allinfo:
            if info!=None:
                name=get(getname)
                url=get(geturl)
                if name and url:
                    data = {'Name': name, 'URL': url}
                    listinfo.append(data)

        response.close()
        return listinfo


dir=gethqpath()
site="{}?tab=art".format(input("Paste url of mangadex content: "))
volumes=getinfo(site, classinfo="group flex items-start relative mb-auto select-none", extrainfo="a", getname="text", geturl="href")
for pos, vol in enumerate(volumes):
    filepath=os.path.join(verifpath(os.path.join(dir, vol["Name"]), 1), Path("Cover").with_suffix(os.path.splitext(vol["URL"])[-1]))
    if verifpath(filepath, 0)==False:
        image_data=getinfo(vol["URL"], mode=1).content
        with open(filepath, 'wb') as img:
            img.write(image_data)
    print('Cover of "{}" done. ({}/{})'.format(vol["Name"], pos+1, len(volumes)), end="\r")
    time.sleep(3)
os.system('cls')
print("All completed.")