import pyexiv2
import pandas as pd
import os
import datetime


def show_modification_date(file_path):
    try:
        # Änderungsdatum der Datei ermitteln
        modification_time = os.path.getmtime(file_path)
        modification_datetime = datetime.datetime.fromtimestamp(modification_time)
        
        # Änderungsdatum im spezifischen Format formatieren
        #formatted_date = modification_datetime.strftime('%d/%m/%Y %H:%M:%S')
        formatted_date = modification_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        return formatted_date
    except FileNotFoundError:
        return "Datei nicht gefunden"
    
def add_description_and_date(base_path, file_paths, prediction):
    nCount = 0
    for name in file_paths:
        imgDescription = prediction[nCount]
        full_path = os.path.join(base_path, name)
        modification_date = show_modification_date(full_path)
        print(f'Änderungsdatum für {full_path}: {modification_date}')
        
        with pyexiv2.Image(full_path) as img:
            data = img.read_xmp()
            data1 = img.read_exif()
            
            # Update EXIF Description if not present
            if 'Exif.Image.ImageDescription' not in data1:
                img.modify_exif({'Exif.Image.ImageDescription': imgDescription})
            
            # Update/Create XMP data if 'CreateDate' not present
            if 'Xmp.xmp.CreateDate' not in data:
                if prediction[nCount] != 'Leer':
                    data.update({
                        'Xmp.xmp.CreateDate': modification_date,
                        'Xmp.xmp.Rating': '2'  # Assuming you want to set Rating to '1'
                    })
                else:
                    data.update({
                        'Xmp.xmp.CreateDate': modification_date,
                        'Xmp.xmp.Rating': '1'  # Assuming you want to set Rating to '1'
                    })
                img.modify_xmp(data)
                
        nCount+=1

# Pfad zur CSV-Datei
csv_path = r'E:\Wildkamera\240810\test\deepfaune.csv'

# CSV lesen und die Dateipfade extrahieren
df = pd.read_csv(csv_path)
file_paths = df['filename'] 
prediction = df['prediction'] 



# Dateipfad (ersetzen Sie diesen mit dem Pfad zur tatsächlichen Datei)
#file_path = r'.\DSCF0259.jpg'

# Änderungsdatum anzeigen
#modification_date = show_modification_date(file_path)
#print(f'Änderungsdatum der Datei: {modification_date}')

#print(data)
#print(file_paths)

# Basispfad, wo die Dateien gespeichert sind (angepasst für Ihr Beispiel)
base_path = r'E:\Wildkamera\240810\101MEDIA'

add_description_and_date(base_path, file_paths, prediction)

    