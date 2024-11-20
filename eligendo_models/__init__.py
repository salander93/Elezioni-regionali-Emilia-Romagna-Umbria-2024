import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
from datetime import datetime

class EligendoScraperIstat:
    def __init__(self, comuni_path):
        self.options = Options()
        self.options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        self.action_chains = ActionChains(self.driver)
        self.comuni_path = comuni_path

        # Crea cartella per il salvataggio se non esiste
        self.data_folder = os.path.join(os.path.expanduser("~"), "Desktop", "dati_elezioni")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def construct_url(self, codice_elettorale):
        """Costruisce l'URL per un comune specifico usando il codice elettorale"""
        base_url = "https://elezioni.interno.gov.it/risultati/20241117/regionali/scrutini/italia/"
        # Aggiungi uno zero all'inizio del codice elettorale
        codice_completo = f"0{codice_elettorale}"
        return f"{base_url}{codice_completo}"

    def extract_data_from_page(self):
        """Estrae i dati dalla pagina corrente"""
        try:
            time.sleep(5)  # Attendi caricamento pagina

            data_rows = []
            current_candidate = None

            # Cerca tutte le righe con nomi (candidati e liste)
            rows = self.driver.find_elements(By.CSS_SELECTOR, "td[rel='nomec']")
            print(f"Trovate {len(rows)} righe con nomi")

            for row in rows:
                try:
                    # Trova la riga padre (tr)
                    parent_row = row.find_element(By.XPATH, "./..")

                    # Cerca nome
                    nome = row.find_element(By.CSS_SELECTOR, "p[align='left']").text.strip()

                    # Cerca voti nella stessa riga
                    voti = parent_row.find_element(By.CSS_SELECTOR,
                                                   "td[rel='votic'] p[align='right']").text.strip().replace('.', '')

                    # Cerca percentuale nella stessa riga
                    percentuale = parent_row.find_element(By.CSS_SELECTOR,
                                                          "td[rel='percc'] p[align='right']").text.strip()

                    if nome and voti:  # Se abbiamo sia nome che voti
                        # Determina se è un candidato o una lista
                        is_candidate = any(word in nome for word in [
                            'DE PASCALE', 'UGOLINI', 'TEODORI', 'SERRA'
                        ])

                        if is_candidate:
                            current_candidate = nome
                            tipo = 'CANDIDATO'
                        else:
                            tipo = 'LISTA'

                        data_rows.append({
                            'data_estrazione': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'tipo': tipo,
                            'candidato_riferimento': current_candidate if tipo == 'LISTA' else '',
                            'nome': nome,
                            'voti': voti,
                            'percentuale': percentuale
                        })
                        print(f"Estratti dati: {nome} - {voti} voti - {percentuale}")

                except Exception as e:
                    print(f"Errore nell'elaborazione di una riga: {e}")
                    continue

            return data_rows

        except Exception as e:
            print(f"Errore nell'estrazione dei dati: {e}")
            return []

    def scrape_all_comuni(self):
        """Scarica i dati per tutti i comuni"""
        print(f"Leggo il file dei comuni da: {self.comuni_path}")
        comuni_df = pd.read_csv(self.comuni_path, sep='\t')

        # Per debug: stampa quali province sono presenti nel file
        print("\nProvince nel file:")
        print(comuni_df['Provincia'].unique())

        all_data = []
        total_comuni = len(comuni_df)
        processed_comuni = 0

        # Ordina i comuni per provincia e nome comune
        comuni_df = comuni_df.sort_values(['Provincia', 'Comune'])

        for _, row in comuni_df.iterrows():
            provincia = row['Provincia']
            comune = row['Comune']
            codice_elettorale = row['Codice elettorale']

            processed_comuni += 1
            print(f"\nProcesso comune {processed_comuni}/{total_comuni}: {comune} ({provincia})")

            try:
                url = self.construct_url(codice_elettorale)
                print(f"URL: {url}")

                self.driver.get(url)
                time.sleep(5)

                comune_data = self.extract_data_from_page()

                if comune_data:
                    for row in comune_data:
                        row['provincia'] = provincia
                        row['comune'] = comune

                    all_data.extend(comune_data)
                    print(f"Estratte {len(comune_data)} righe per {comune}")
                else:
                    print(f"Nessun dato trovato per {comune}")

            except Exception as e:
                print(f"Errore nel processare {comune}: {e}")
                continue

        return all_data

    def save_to_csv(self, data, filename):
        """Salva i dati in CSV"""
        if not data:
            print("Nessun dato da salvare")
            return

        fieldnames = [
            'data_estrazione', 'provincia', 'comune',
            'tipo', 'candidato_riferimento', 'nome', 'voti', 'percentuale'
        ]

        filepath = os.path.join(self.data_folder, filename)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(data)
            print(f"\nDati salvati con successo in: {filepath}")

            # Stampa alcune statistiche
            df = pd.DataFrame(data)
            print("\nStatistiche finali:")
            print(f"Totale righe: {len(df)}")
            print(f"Comuni elaborati: {df['comune'].nunique()}")
            print("\nComuni per provincia:")
            print(df.groupby('provincia')['comune'].nunique())

        except Exception as e:
            print(f"Errore nel salvare il file CSV: {e}")

    def close(self):
        self.driver.quit()
