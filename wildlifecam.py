import pyexiv2
import pandas as pd
import os
import datetime


def show_modification_date(file_path):
    # Änderungsdatum der Datei ermitteln
    modification_time = os.path.getmtime(file_path)
    modification_datetime = datetime.datetime.fromtimestamp(modification_time)

    # Änderungsdatum als String formatieren
    #formatted_date = modification_datetime.strftime('%d/%m/%Y %H:%M:%S')
    formatted_date = modification_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]  # Schneidet die letzten drei Zeichen der Mikrosekunden ab
    return formatted_date


# Dateipfad (ersetzen Sie diesen mit dem Pfad zur tatsächlichen Datei)
file_path = r'.\DSCF0259.jpg'

# Änderungsdatum anzeigen
modification_date = show_modification_date(file_path)
print(f'Änderungsdatum der Datei: {modification_date}')

with pyexiv2.Image(r'.\DSCF0259.jpg') as img:
    data = img.read_xmp()
    data = {'Xmp.xmp.CreateDate': modification_date,   # Assign a value to a tag. This will overwrite its original value, or add it if it doesn't exist
        'Xmp.xmp.Rating': None}                            # Assign None to delete the tag
    img.modify_xmp(data)

print(data)