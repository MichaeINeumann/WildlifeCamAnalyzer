import pyexiv2
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt


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

def add_create_date_to_csv(csv_path, base_path):
    # CSV lesen
    df = pd.read_csv(csv_path)
    create_dates = []

    # Erstelldatum für jede Datei extrahieren
    for filename in df['filename']:
        full_path = os.path.join(base_path, filename)
        if os.path.exists(full_path):
            modification_date = show_modification_date(full_path)
            create_dates.append(modification_date)
        else:
            create_dates.append("Datei nicht gefunden")
    
    # Neue Spalte hinzufügen
    df['CreateDate'] = create_dates
    df.to_csv(csv_path, index=False)
    
def add_xmp_create_date_to_csv(csv_path, base_path):
    # CSV lesen
    df = pd.read_csv(csv_path)
    create_dates = []

    # Erstelldatum aus XMP-Daten für jede Datei extrahieren
    for filename in df['filename']:
        full_path = os.path.join(base_path, filename)
        if os.path.exists(full_path):
            try:
                with pyexiv2.Image(full_path) as img:
                    data = img.read_xmp()
                    # Überprüfen, ob das 'CreateDate' bereits vorhanden ist
                    if 'Xmp.xmp.CreateDate' in data:
                        create_dates.append(data['Xmp.xmp.CreateDate'])
                    else:
                        create_dates.append("Erstellungsdatum nicht gefunden")
            except Exception as e:
                create_dates.append(f"Fehler beim Lesen der Metadaten: {e}")
        else:
            create_dates.append("Datei nicht gefunden")
    
    # Neue Spalte hinzufügen
    df['CreateDate'] = create_dates
    df.to_csv(csv_path, index=False)
    
def plot_animal_activity(csv_path, time_threshold=10):
    # CSV lesen
    df = pd.read_csv(csv_path)
    
    # Datum und Zeit extrahieren und in datetime umwandeln
    df['DateTime'] = pd.to_datetime(df['CreateDate'])
    
    # Stunde und Minute extrahieren
    df['Hour'] = df['DateTime'].dt.hour
    df['Minute'] = df['DateTime'].dt.minute
    
    # Gruppierung und Deduplizierung
    df = df.sort_values(by=['DateTime'])
    df['TimeDiff'] = df.groupby('prediction')['DateTime'].diff().dt.total_seconds().div(60).fillna(0)
    df = df[(df['TimeDiff'] > time_threshold) | (df['TimeDiff'] == 0)]

    # Aktivitäten nach Tierart und Stunde zählen
    plt.figure(figsize=(12, 8))
    for animal in df['prediction'].unique():
        hourly_activity = df[(df['prediction'] == animal)].groupby('Hour').size()
        plt.plot(hourly_activity.index, hourly_activity, label=animal, marker='o')
    
    plt.xlabel('Stunde des Tages')
    plt.ylabel('Anzahl der Aktivitäten')
    plt.title('Aktivitäten der Tierarten nach Uhrzeit')
    plt.legend()
    plt.grid(True)
    plt.show()
    
def plot_individual_animal_activity(csv_path, time_threshold=10):
    # CSV lesen
    df = pd.read_csv(csv_path)
    
    # Datum und Zeit extrahieren und in datetime umwandeln
    df['DateTime'] = pd.to_datetime(df['CreateDate'])
    
    # Stunde und Minute extrahieren
    df['Hour'] = df['DateTime'].dt.hour
    
    # Gruppierung und Deduplizierung
    df = df.sort_values(by=['DateTime'])
    df['TimeDiff'] = df.groupby('prediction')['DateTime'].diff().dt.total_seconds().div(60).fillna(0)
    df = df[(df['TimeDiff'] > time_threshold) | (df['TimeDiff'] == 0)]

    # Aktivitäten nach Tierart und Stunde zählen
    animal_types = df['prediction'].unique()
    for animal in animal_types:
        plt.figure(figsize=(10, 6))
        hourly_activity = df[df['prediction'] == animal].groupby('Hour').size()
        hourly_activity = hourly_activity.reindex(range(24), fill_value=0)
        plt.bar(hourly_activity.index, hourly_activity, color='skyblue')
        
        plt.xlabel('Stunde des Tages')
        plt.ylabel('Anzahl der Aktivitäten')
        plt.title(f'Aktivitäten von {animal} nach Uhrzeit')
        plt.xticks(range(24))  # Stellen Sie sicher, dass alle Stunden angezeigt werden
        plt.grid(True)
        plt.show()
        
def save_individual_animal_activity_plots(csv_path, output_folder, time_threshold=10):
    # CSV lesen
    df = pd.read_csv(csv_path)
    
    # Datum und Zeit extrahieren und in datetime umwandeln
    df['DateTime'] = pd.to_datetime(df['CreateDate'])
    
    # Stunde und Minute extrahieren
    df['Hour'] = df['DateTime'].dt.hour
    
    # Gruppierung und Deduplizierung
    df = df.sort_values(by=['DateTime'])
    df['TimeDiff'] = df.groupby('prediction')['DateTime'].diff().dt.total_seconds().div(60).fillna(0)
    df = df[(df['TimeDiff'] > time_threshold) | (df['TimeDiff'] == 0)]

    # Datenbereich für den Titel ermitteln
    start_date = df['DateTime'].min().strftime('%Y-%m-%d')
    end_date = df['DateTime'].max().strftime('%Y-%m-%d')
    date_range = f'{start_date} bis {end_date}'

    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Aktivitäten nach Tierart und Stunde zählen
    animal_types = df['prediction'].unique()
    for animal in animal_types:
        plt.figure(figsize=(10, 6))
        hourly_activity = df[df['prediction'] == animal].groupby('Hour').size()
        hourly_activity = hourly_activity.reindex(range(24), fill_value=0)
        plt.bar(hourly_activity.index, hourly_activity, color='skyblue')
        
        plt.xlabel('Stunde des Tages')
        plt.ylabel('Anzahl der Aktivitäten')
        plt.title(f'Aktivitäten von {animal} nach Uhrzeit ({date_range})')
        plt.xticks(range(24))  # Stellen Sie sicher, dass alle Stunden angezeigt werden
        plt.grid(True)
        
        # Speichern des Diagramms als Bild
        plt.savefig(os.path.join(output_folder, f'{animal}_activity_{date_range}.png'), dpi=300)
        plt.close()  # Schließt das aktuelle Diagramm, um Ressourcen freizugeben

# Pfad zur CSV-Datei
csv_path = r'E:\Wildkamera\240810\100MEDIA\deepfaune.csv'
# Basispfad, wo die Dateien gespeichert sind (angepasst für Ihr Beispiel)
base_path = r'E:\Wildkamera\240810\100MEDIA'

#output_folder = r'E:\Wildkamera\plots'  # Stellen Sie sicher, dass dieser Pfad existiert oder angelegt wird
output_folder = base_path

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




add_description_and_date(base_path, file_paths, prediction)

add_xmp_create_date_to_csv(csv_path, base_path)

#plot_animal_activity(csv_path)
#plot_individual_animal_activity(csv_path)
save_individual_animal_activity_plots(csv_path, output_folder)
    