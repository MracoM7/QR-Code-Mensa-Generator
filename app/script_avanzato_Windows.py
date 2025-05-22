from datetime import date
from bs4 import BeautifulSoup
import re
import qrcode 
import random
import requests
import getpass

# Costanti
luogo = "Pg-Ingegneria"
presenza_asporto = "In presenza" 
menu_tipo = "STANDARD"
path = ".\\app\\"

def getMenu():
    # Inserisci qui le tue credenziali
    USERNAME = input("Username: ")
    PASSWORD = getpass.getpass("Password: ")

    # URL del login e del menu
    LOGIN_URL = 'https://intragenzia.adisu.umbria.it/user/login'
    MENU_ODIERNI_URL = 'https://intragenzia.adisu.umbria.it/menu-odierni'
    BASE_MENU_URL = 'https://intragenzia.adisu.umbria.it'  

   # Inizializza la sessione
    session = requests.Session()

    # Ottieni la pagina di login per i token hidden
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    # Estrai i valori dei campi hidden
    form_build_id = soup.find('input', {'name': 'form_build_id'})['value']
    form_id = soup.find('input', {'name': 'form_id'})['value']

    # Prepara i dati di login
    login_data = {
        'name': USERNAME,
        'pass': PASSWORD,
        'form_build_id': form_build_id,
        'form_id': form_id,
        'op': 'Accedi'
    }

    # Invia la richiesta di login
    response = session.post(LOGIN_URL, data=login_data)

    # Controlla se il login ha avuto successo
    if "logout" in response.text.lower():
        print("Login effettuato con successo!")


        #Naviga alla pagina dei menu odierni
        menu_odierni_page = session.get(MENU_ODIERNI_URL)
        menu_odierni_soup = BeautifulSoup(menu_odierni_page.text, 'html.parser')

        # Estrai il testo dalla pagina dei menu odierni
        text = menu_odierni_soup.get_text(separator=" ", strip=True)
        
        
        # Estrai il link node collegato Mensa Ingegneria
        link = menu_odierni_soup.find('a', href=True, string=lambda x: "Mensa Ingegneria" in x)
        if link:
            # Estrai l'URL completo
            menu_url = link['href']
            MENU_URL = BASE_MENU_URL + menu_url
            #print(f"Link al menu: {MENU_URL}")
        else:
            print("Link al menu non trovato.")
            return None        

        # Naviga alla pagina del menu
        menu_page = session.get(MENU_URL)
        menu_soup = BeautifulSoup(menu_page.text, 'html.parser')

        # Estrai tutto il testo dalla pagina del menu
        text = menu_soup.get_text(separator=" ", strip=True)

        # Trova la sezione desiderata
        start_marker = "Menù Primi piatti :"
        end_marker = "rotazione Prenotazione"

        start_index = text.find(start_marker)
        end_index = text.find(end_marker)

        if start_index != -1 and end_index != -1:
            raw_menu = text[start_index:end_index]

            # Aggiunge spazi dove manca tra minuscola e maiuscola (es: "melanzaneINSALATA" → "melanzane INSALATA")
            fixed_menu = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw_menu)

            # A capo dopo ogni sezione
            fixed_menu = fixed_menu.replace("Primi piatti : ", "\nPrimi piatti:\n") \
                                .replace("Secondi piatti : ", "\nSecondi piatti:\n") \
                                .replace("Contorni : ", "\nContorni:\n") \
                                .replace("Frutta : ", "\nFrutta:\n") \
                                .replace("Dessert : ", "\nDessert:\n")\
                                .replace("Dessert vari a", "Dessert vari a rotazione")
            
            #A capo per ogni portata
            fixed_menu = re.sub(r'(?<!^)(?<!\n)(\s)([A-Z])', r'\n\2', fixed_menu)

            # Rimuove le righe vuote
            fixed_menu = re.sub(r'\n\s*\n', '\n', fixed_menu)

            # Fix Insalata Mista in CAPSLOCK che va a capo
            fixed_menu = fixed_menu.replace("INSALATA\nMISTA", "INSALATA MISTA")

            # Stampa il risultato
            #print(fixed_menu.strip())
            return fixed_menu.strip()

        else:
            print("Sezione non trovata nel testo.")
            return None

    else:
        print("Login fallito.")
        return None

def generaCodice():
    # Genera un codice casuale di 6 cifre
    seed = 336000
    data_seed = "2025-05-06"
    data = date.today()
    if data > date.fromisoformat(data_seed):
        codice = seed + 2000*(data - date.fromisoformat(data_seed)).days + random.randint(1, 999) - 2000 * ((data - date.fromisoformat(data_seed)).days % 7)
        
    else:
        codice = seed + random.randint(1, 1999)
    return str(codice).zfill(6)

def generaTXT():
    with open(path + "res\\mensa.txt", "w") as file:
        file.write(f"{data_file}\nCodice: {codice}\nPranzo\n{primo_piatto}\n{secondo_piatto}\n{contorno}\n{frutta}\n{dessert}")  

def generaQR():
    with open(path + "res\\mensa.txt", "r") as file:
        data = file.read()
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0,
        
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(154,95,0), back_color="white")
    img.save(path + "res\\qrcode.png")

def generaHTML(codice, data, primo_piatto, secondo_piatto, contorno, frutta, dessert):

    # Leggi il file HTML originale
    with open(path + "res\\base.html", "r", encoding="utf-8") as file:
        html = file.read()

    # Parsing con BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Modifica il codice pranzo nel titolo e nel badge
    # Titolo della pagina (h1)
    titolo = soup.find("h1")
    if titolo and titolo.span:
        testo_titolo = titolo.span.text
        nuovo_titolo = f"Codice Pranzo {codice} - {data} - {luogo}"
        titolo.span.string = nuovo_titolo

    # Modifica anche il tag title
    title_tag = soup.find("title")
    if title_tag:
        title_tag.string = f"Codice Pranzo {codice} - {data} - {luogo} | IntrAgenzia A.Di.S.U."

    # Badge del codice
    badge = soup.find("div", class_="badge")
    if badge:
        badge.string = codice

    # Modifica i campi del menu
    # Presenza/Asporto
    presenza_field = soup.find("div", class_="field--name-field-presenza")
    if presenza_field:
        valore = presenza_field.find_all("div")[1]
        if valore:
            valore.string = presenza_asporto

    # Tipo di menu
    menu_field = soup.find("div", class_="field--name-field-scelta-del-menu")
    if menu_field:
        valore = menu_field.find_all("div")[1]
        if valore:
            valore.string = menu_tipo

    # Primo piatto
    primi_field = soup.find("div", class_="field--name-field-primi-piatti")
    if primo_piatto == "[node:field_primi_piatti:entity]" and primi_field:
        primi_field.decompose()   
    else:
        if primi_field:
            valore = primi_field.find_all("div")[1].find("div")
            if valore:
                valore.string = primo_piatto

    # Secondo piatto
    secondi_field = soup.find("div", class_="field--name-field-secondi-piatti")
    if secondo_piatto == "[node:field_secondi_piatti:entity]" and secondi_field:
        secondi_field.decompose()
    else:
        if secondi_field:
            valore = secondi_field.find_all("div")[1].find("div")
            if valore:
                valore.string = secondo_piatto

    # Contorno
    contorno_field = soup.find("div", class_="field--name-field-contorni")
    if contorno == "[node:field_contorni:entity]" and contorno_field:
        contorno_field.decompose()
    else:
        if contorno_field:
            valore = contorno_field.find_all("div")[1].find("div")
            if valore:
                valore.string = contorno

    # Frutta
    frutta_field = soup.find("div", class_="field--name-field-frutta")
    if frutta == "[node:field_frutta:entity]" and frutta_field:
        frutta_field.decompose()
    else:
        if frutta_field:
            valore = frutta_field.find_all("div")[1].find("div")
            if valore:
                valore.string = frutta

    # Dessert
    dessert_field = soup.find("div", class_="field--name-field-dessert")
    if dessert == "[node:field_dessert:entity]" and dessert_field:
        dessert_field.decompose()
    else:
        if dessert_field:
            valore = dessert_field.find_all("div")[1].find("div")
            if valore:
                valore.string = dessert


    # Modifica l'attributo data-history-node-id per evitare conflitti
    node_div = soup.find("div", attrs={"data-history-node-id": True})
    if node_div:
        node_div["data-history-node-id"] = codice

    # Scrivi il nuovo HTML su file
    with open(path + "mensa.html", "w", encoding="utf-8") as file:
        file.write(str(soup))

def prenotazione(menu):
    lista_primi = []
    lista_secondi = []
    lista_contorni = []
    lista_frutta = []
    lista_dessert = []

    # Estrai le portate dal menu
    portate = menu.split("\n")
    for p in portate:
        if "Primi piatti:" in p:
            i = portate.index(p)
            for primi in portate[i+1:]:
                if "Secondi piatti:" in primi:
                    break
                lista_primi.append(primi) 

        elif "Secondi piatti:" in p:
            i = portate.index(p)
            for secondi in portate[i+1:]:
                if "Contorni:" in secondi:
                    break
                lista_secondi.append(secondi) 

        elif "Contorni:" in p:
            i = portate.index(p)
            for contorni in portate[i+1:]:
                if "Frutta:" in contorni:
                    break
                lista_contorni.append(contorni) 

        elif "Frutta:" in p:    
            i = portate.index(p)
            for frutta in portate[i+1:]:
                if "Dessert:" in frutta:
                    break
                lista_frutta.append(frutta) 

        elif "Dessert:" in p:
            i = portate.index(p)
            for dessert in portate[i+1:]:
                lista_dessert.append(dessert)


    # Inizializza le variabili per le portate
    primo_piatto = "[node:field_primi_piatti:entity]"
    secondo_piatto = "[node:field_secondi_piatti:entity]"
    contorno = "[node:field_contorni:entity]"
    frutta = "[node:field_frutta:entity]"
    dessert = "[node:field_dessert:entity]"


    # Seleziona il piatto desiderato tramite riga di comando (0 se non si vuole selezionare)
    print("\nSeleziona il primo desiderato (0 per non selezionare):")
    for i, portata in enumerate(lista_primi):
        print(f"{i + 1}: {portata}")
    scelta_primo = int(input("Scelta primo piatto: ")) - 1
    if scelta_primo >= 0 and scelta_primo < len(lista_primi):
        primo_piatto = lista_primi[scelta_primo]
    
    print("\nSeleziona il secondo desiderato (0 per non selezionare):")
    for i, portata in enumerate(lista_secondi):
        print(f"{i + 1}: {portata}")
    scelta_secondo = int(input("Scelta secondo piatto: ")) - 1
    if scelta_secondo >= 0 and scelta_secondo < len(lista_secondi):
        secondo_piatto = lista_secondi[scelta_secondo]
    
    print("\nSeleziona il contorno desiderato (0 per non selezionare):")
    for i, portata in enumerate(lista_contorni):
        print(f"{i + 1}: {portata}")
    scelta_contorno = int(input("Scelta contorno: ")) - 1
    if scelta_contorno >= 0 and scelta_contorno < len(lista_contorni):
        contorno = lista_contorni[scelta_contorno]
    
    print("\nSeleziona la frutta desiderata (0 per non selezionare):")
    for i, portata in enumerate(lista_frutta):
        print(f"{i + 1}: {portata}")
    scelta_frutta = int(input("Scelta frutta: ")) - 1
    if scelta_frutta >= 0 and scelta_frutta < len(lista_frutta):
        frutta = lista_frutta[scelta_frutta]
    
    if frutta == "[node:field_frutta:entity]":
        # Se la frutta è stata selezionata, non mostrare il dessert
        print("\nSeleziona il dessert desiderato (0 per non selezionare):")
        for i, portata in enumerate(lista_dessert):
            print(f"{i + 1}: {portata}")
        scelta_dessert = int(input("Scelta dessert: ")) - 1
        if scelta_dessert >= 0 and scelta_dessert < len(lista_dessert):
            dessert = lista_dessert[scelta_dessert]

    return primo_piatto, secondo_piatto, contorno, frutta, dessert
    
# Prendi il Menu dal sito
menu = getMenu()
#print(menu)


if menu: # Se il menu è stato recuperato con successo

    # Parametri configurabili
    codice = generaCodice()
    data = date.today().strftime("%d/%m/%y")
    data_file = date.today().strftime("%d/%m%Y")


    primo_piatto, secondo_piatto, contorno, frutta, dessert = prenotazione(menu)
    generaTXT()
    generaQR()
    generaHTML(codice, data, primo_piatto, secondo_piatto, contorno, frutta, dessert)

    

    print(f"Modifiche completate! Codice pranzo: {codice}, Data: {data}")

else:
    print("Errore nel recupero del menu")
