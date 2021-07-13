import requests
from bs4 import BeautifulSoup as bs
import regex as re
import xlsxwriter
import sys, getopt

#URL = 'https://paperswithcode.com/paper/skweak-weak-supervision-made-easy-for-nlp'
#URL = 'https://paperswithcode.com/paper/mbrl-lib-a-modular-library-for-model-based'
URL = 'https://paperswithcode.com/paper/videogpt-video-generation-using-vq-vae-and'
#URL = 'https://paperswithcode.com/paper/emerging-properties-in-self-supervised-vision'


def body(URL):
    respuesta = requests.get(URL)
    soup = bs(respuesta.content, 'html.parser')
    body = soup.find('body')
    return body

def getTitle(URL):
    titulo = body(URL).find("div", class_ = 'paper-title').find('h2').text
    titulo = re.sub(r'^\s*','', titulo).split('\n')[0]
    return titulo

def getAbstract(URL):
    abstract = body(URL).find("div", class_ = 'paper-abstract').find('p').text
    # Para eliminar el (read more) que hay en todas y además eliminar los espacios del principio
    abstract = ''.join(re.sub(r'^\s*','', abstract).split("\n")[:-2])
    return abstract

# Los metodos se guardan en un diccionario, donde la clave es el nombre del metodo, seguidos por una lista que contiene su link y su definicion
def getMetodos(URL):
    metodos = body(URL).find("div", class_ = 'method-section').find_all('a')
    diccionario = {}
    nombre = ''

    for i in metodos:
        nombre =  re.sub(r'^\s*','', i.text)#.split('\n')[0]
        if nombre.startswith('relevant methods here'):
            return None
        link = 'https://paperswithcode.com' + i['href']
        
        definicion = getDefinicionMetodo(link)
        diccionario[nombre] = [link, definicion]
    return diccionario

# Funcion que dado un link de un metodo obtiene la definicion de dicho metodo en una cadena
def getDefinicionMetodo(link):

    lAux = body(link).find('div', class_ = 'method-content').find('div', class_ = 'row').find_all('p')
    resultado = ''
    for element in lAux:
        resultado = resultado + element.text + '\n'
    return resultado

def getPDF(URL):
    linkPdf = body(URL).find('div', class_ = 'paper-abstract').find('a', class_ = 'badge badge-light')['href']
    return linkPdf

def getCode(URL):
    linkCode = body(URL).find('div', class_ = 'paper-implementations code-table').find('a', class_ = 'code-table-link')['href']
    return linkCode

def getAuthors(URL):
    authors = body(URL).find('div', class_ = 'authors').find_all(class_ = 'author-span')
    authors = [author.text.replace('\n','').replace('  ','') for author in authors][1:]
    return authors

def getFechaPub(URL):
    lista = body(URL).find('div', class_ = 'authors').find_all(class_ = 'author-span')
    fechaPub = [author.text.replace('\n','').replace('  ','') for author in lista][0]
    return fechaPub

def exportToExcel(titulo, abstract, metodos, nombre_output, pdf_link, code_link, authors, fechaPub):
    
    workbook = xlsxwriter.Workbook(nombre_output + '.xlsx')

    # Para que el nombre del worksheet sea valido hay que eliminar ciertos caracteres y solo se permite de 31 hasta longitud
    nombre_worksheet = titulo.replace('[','').replace(']','').replace(':','').replace('*','').replace('*','').replace('?','').replace('/','').replace('\\','')[:31]
    worksheet = workbook.add_worksheet(nombre_worksheet)

    # Para cuando queramos aniadir en negrita cosas, simplemente se le pasa el barametro 'bold' como tercer argumento
    bold = workbook.add_format({'bold': True})
    
    # Aqui es donde se va a escribir la informacion respectiva al paper
    worksheet.write('A1', 'TITULO', bold)
    worksheet.write('B1', 'ABSTRACT', bold)
    worksheet.write('C1', 'PAPER_LINK', bold)
    worksheet.write('D1', 'PDF_LINK', bold)
    worksheet.write('E1', 'CODE_LINK', bold)
    worksheet.write('F1', 'AUTHORS', bold)
    worksheet.write('G1', 'FECHA_PUB', bold)

    worksheet.write('A2', titulo)
    worksheet.write('B2', abstract)
    worksheet.write('C2', URL)
    worksheet.write('D2', pdf_link)
    worksheet.write('E2', code_link)
    worksheet.write('F2', str(authors))
    worksheet.write('G2', fechaPub)

    # Aqui empieza donde se va a escribir la informacion respectiva a los metodos
    if metodos is not None:
        worksheet.write('B4', 'Nombre', bold)
        worksheet.write('C4', 'Link', bold)
        worksheet.write('D4', 'Definicion', bold)

        fila, columna = 4, 0

        for nombre in metodos:
            worksheet.write(fila, columna, 'MET ' + str(fila-3), bold)
            worksheet.write(fila, columna + 1, nombre)
            worksheet.write(fila, columna + 2, metodos[nombre][0])
            worksheet.write(fila, columna + 3, metodos[nombre][1])
            fila += 1    
            
    workbook.close()

def main():
    global URL
    nombre_output = 'output'
    # Catch porque a veces puede fallar al llamar el multiple papers debido que nos lleva a alguna que otra pagina
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:],'o:l:', ["ofile=", "link="])
        except getopt.GetoptError:
            print('python3 papers_ws -o <outputfile> -l <linkMethod>')
            return
        for opt, arg in opts:
            if opt == '-h':
                print('python3 papers_ws -o <outputfile> -l <linkMethod>')
                return
            elif opt in ('-o', '--ofile'):
                nombre_output = arg
            elif opt in ('-l', '--link'):
                URL = arg

        titulo = getTitle(URL)
        abstract = getAbstract(URL)
        metodos = getMetodos(URL)
        pdf_link = getPDF(URL)
        code_link = getCode(URL)
        authors = getAuthors(URL)
        fechaPub = getFechaPub(URL)

        exportToExcel(titulo, abstract, metodos, nombre_output, pdf_link, code_link, authors, fechaPub)
        print('Fichero ' + nombre_output +'.xlsx creado con exito del paper: ' + titulo)
    except:
        print('WARNING: No se ha podido realizar correctamente la extraccion de ' + str(URL))

if __name__ == "__main__": 
    main()


