import requests
from bs4 import BeautifulSoup as bs
import os

# Cuando se van a introducir varias palabras se tienen que separar por espacios
URL = 'https://paperswithcode.com/search?q_meta=&q_type=&q='


def body(URL):
    respuesta = requests.get(URL)
    soup = bs(respuesta.content, 'html.parser')
    body = soup.find('body')
    return body

def get_links(URL):
    lista = body(URL).find("div", class_ = 'infinite-container text-center').find_all("div", class_ = 'col-lg-3 item-image-col')
    
    index = 0
    for elem in lista:

        try:
            concat = elem.find('a')['href']
            lista[index] = 'https://paperswithcode.com' + concat
            index+=1
        except Exception:
            continue
    return lista

def main():
    global URL
    palabras = input('Introduzca la palabra/frase por la que desea buscar papers:\n')

    palabras = palabras.replace(' ','+')
    URL = URL + palabras
    
    print('Buscando y haciendo metodo de busqueda...')
    lista = get_links(URL)

    n = 1

    
    
    
    lista = [element for element in lista if str(element).startswith('https://paperswithcode.com')]

    for link in lista:
        try:
            os.system('python3 paper_ws.py -o ' + str(n) + ' -l ' + link)
            n += 1
        except:
            n += 1

    if len(lista) == 0:
        print('ATENCION: No se encontro ningun paper relacionado con las palabras indicadas')

if __name__ == "__main__":
    main()