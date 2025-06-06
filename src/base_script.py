from datetime import date
from pathlib import Path
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
path = str(Path(__file__).resolve().parent) + "/"


def generaCodice(seed):
    # Genera un codice basato su un codice seed
    codice = seed - seed//1000 + random.randint(0, 999)
    return str(codice).zfill(6)

def generaTXT():
    with open(path + "generated/mensa.txt", "w") as file:
        file.write(f"{data_file}\nCodice: {codice}\nPranzo\n{primo_piatto}\n{secondo_piatto}\n{contorno}\n{frutta}\n{dessert}")  

def generaQR():
    with open(path + "generated/mensa.txt", "r") as file:
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
    img.save(path + "generated/qrcode.png")

def generaHTML(codice, data, primo_piatto, secondo_piatto, contorno, frutta, dessert):

    # Leggi il file HTML originale
    with open(path + "res/base.html", "r", encoding="utf-8") as file:
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
    with open(path + "generated/mensa.html", "w", encoding="utf-8") as file:
        file.write(str(soup))



if __name__ == "__main__":
    # Parametri configurabili
    codice = generaCodice(int(input("Inserisci un codice seed (numero): ")))

    if not codice.isdigit() or len(codice) != 6:
        raise ValueError("Il codice deve essere un numero di 6 cifre.")

    data = date.today().strftime("%d/%m/%y")
    data_file = date.today().strftime("%d/%m%Y")

    primo_piatto = input("Primo: ")
    secondo_piatto = input("Secondo: ")
    contorno = input("Contorno: ")
    frutta = "[node:field_frutta:entity]"
    dessert = "[node:field_dessert:entity]"

    generaTXT()
    generaQR()
    generaHTML(codice, data, primo_piatto, secondo_piatto, contorno, frutta, dessert)



    print(f"Modifiche completate! Codice pranzo: {codice}, Data: {data}")