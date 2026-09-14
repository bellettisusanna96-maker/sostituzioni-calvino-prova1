import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestione Sostituzioni I.I.S. Calvino", layout="wide", page_icon="🏫")

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

# Mappatura delle 44 Classi e relativi Indirizzi
CLASSES_INFO = {
    # Liceo Scientifico (LS)
    '1A': 'LS', '2A': 'LS', '3A': 'LS', '4A': 'LS', '5A': 'LS',
    '1B': 'LS', '2B': 'LS', '3B': 'LS', '4B': 'LS', '5B': 'LS',
    # Liceo Scienze Umane (LSU)
    '1D': 'LSU', '2D': 'LSU', '3D': 'LSU', '4D': 'LSU', '5D': 'LSU',
    '1E': 'LSU', '2E': 'LSU', '3E': 'LSU',
    '1F': 'LSU', '2F': 'LSU', '3F': 'LSU', '4F': 'LSU', '5F': 'LSU',
    '1H': 'LSU', '2H': 'LSU', '3H': 'LSU', '4H': 'LSU',
    # Istituto Tecnico Economico (ITE)
    '1a': 'ITE', '2a': 'ITE', '3a': 'ITE', '4a': 'ITE', '5a': 'ITE',
    '1b': 'ITE', '2b': 'ITE', '3b': 'ITE', '4b': 'ITE', '5b': 'ITE',
    '1c': 'ITE', '2c': 'ITE', '3c': 'ITE', '4c': 'ITE', '5c': 'ITE',
    '3d': 'ITE', '3e': 'ITE'
}

# Database completo Docenti, Materia, Indirizzo principale e Consigli di Classe (CdC)
DOCENTI_DB = {
    "ACCIAVATTI Luciana": {"materia": "Filosofia e Storia", "indirizzo": "LS", "cdc": ["3B", "4B", "5B", "4H"]},
    "AGORINI": {"materia": "Lab. Informatica", "indirizzo": "ITE", "cdc": ["3c", "4c", "5c"]},
    "AIRAGHI Eliseo": {"materia": "Scienze Umane / Filosofia", "indirizzo": "LSU", "cdc": ["1E", "1F", "4F", "5F", "4H"]},
    "ALBANESE Alessandra": {"materia": "Geografia", "indirizzo": "ITE", "cdc": ["1a", "2a", "1b", "2b", "1c", "2c"]},
    "ALESSANDRINI": {"materia": "Informatica", "indirizzo": "ITE", "cdc": ["3e"]},
    "AQUINI Simona": {"materia": "Diritto ed Economia", "indirizzo": "ITE", "cdc": ["1b", "5b", "4c"]},
    "ARMELLINO Carla": {"materia": "Scienze Naturali", "indirizzo": "LS", "cdc": ["1A", "2A", "1D", "2D", "3D", "4D", "5D", "3H", "4H"]},
    "AUTERI Mercedes": {"materia": "Storia dell'Arte", "indirizzo": "LSU", "cdc": ["3D", "4D", "5D", "4F", "5F", "3H", "4H"]},
    "BALDINI Martina": {"materia": "Scienze Umane", "indirizzo": "LSU", "cdc": ["2E", "3E", "2F", "3F"]},
    "BALDINI Mauro": {"materia": "Italiano e Storia", "indirizzo": "ITE", "cdc": ["1c", "2c", "3c"]},
    "BARRACO Maria Laura": {"materia": "Italiano e Latino", "indirizzo": "LS", "cdc": ["1B", "5B", "2F"]},
    "BELLETTI Susanna": {"materia": "Scienze Motorie", "indirizzo": "ITE", "cdc": ["1b", "2b", "3b", "4b", "5b", "3c", "4c", "5c", "3e"]},
    "BONCALDO Anna Angela": {"materia": "Inglese", "indirizzo": "LSU", "cdc": ["1D", "2D", "3D", "4D", "1E", "1F"]},
    "BONDESAN": {"materia": "Italiano e Latino", "indirizzo": "LSU", "cdc": ["1F", "3E", "4H"]},
    "BONO Lamberto": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["1a", "3a", "5a"]},
    "BRESCIA Giulia": {"materia": "Inglese", "indirizzo": "LSU", "cdc": ["3c", "2F", "3F", "4F", "5F", "2H"]},
    "BUCCI Stefania": {"materia": "Diritto ed Economia", "indirizzo": "ITE", "cdc": ["1a", "2a", "3a", "4a", "5c"]},
    "CACCIUOTTOLO Adalgisa": {"materia": "Filosofia e Storia", "indirizzo": "LS", "cdc": ["3A", "3F", "4F", "5F"]},
    "CALATAFIMI Federica": {"materia": "Matematica", "indirizzo": "LSU", "cdc": ["1E", "2E", "1F", "2F", "1H", "2H"]},
    "CAMBIELLI": {"materia": "Storia dell'Arte", "indirizzo": "LSU", "cdc": ["3E", "3F"]},
    "CAPONE Maurizio": {"materia": "Italiano e Geostoria", "indirizzo": "LSU", "cdc": ["2A", "1D", "1E", "3H"]},
    "CASALI Federico": {"materia": "Scienze Motorie", "indirizzo": "ITE", "cdc": ["1a", "2a", "3a", "4a", "5a", "1c", "2c", "3d", "4H"]},
    "CATTANEI Giuseppe": {"materia": "Diritto ed Economia", "indirizzo": "ITE", "cdc": ["2b", "3c", "5a", "3d"]},
    "COMINI Fabio": {"materia": "Filosofia e Storia", "indirizzo": "LS", "cdc": ["4A", "5A", "3D", "4D"]},
    "DE CASTRO Calogero": {"materia": "Scienze Motorie", "indirizzo": "LS", "cdc": ["1A", "2A", "3A", "4A", "5A", "1B", "3B", "4B", "5B"]},
    "DE TURSI": {"materia": "Scienze Naturali", "indirizzo": "ITE", "cdc": ["1a", "1b", "2b", "1c", "2c"]},
    "DEMURU Paola": {"materia": "Italiano e Storia", "indirizzo": "ITE", "cdc": ["3b", "4b", "5b"]},
    "DI NUNNO Gaetana": {"materia": "Inglese", "indirizzo": "ITE", "cdc": ["4c", "5c"]},
    "DOCENTE W": {"materia": "Geostoria / Italiano", "indirizzo": "LSU", "cdc": ["2D", "1F", "3F", "2H"]},
    "DOLZAN Manuela": {"materia": "Scienze Naturali", "indirizzo": "LS", "cdc": ["3A", "4A", "5A"]},
    "FAVORITO Francesca": {"materia": "Francese", "indirizzo": "ITE", "cdc": ["3b", "4b", "5b"]},
    "FEDELI Angelo": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["2b", "2c", "3d"]},
    "FELICETTI Monica": {"materia": "Inglese", "indirizzo": "LS", "cdc": ["1B", "2B", "3B", "4B", "5B", "5D"]},
    "GIANNINO Alberto Antonio": {"materia": "Scienze Motorie", "indirizzo": "LSU", "cdc": ["1D", "2D", "3D", "4D", "5D", "3E", "2F", "3F"]},
    "GIANNUZZO Nadia": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["3b", "4b", "5b"]},
    "GIGANTE Gloria": {"materia": "Inglese", "indirizzo": "LSU", "cdc": ["1c", "2c", "3d", "2E", "3E", "4H"]},
    "GIOTTA Tiziana": {"materia": "Informatica", "indirizzo": "ITE", "cdc": ["2a", "2c", "3c", "4c", "5c"]},
    "GRANATA Roberta": {"materia": "Italiano e Latino", "indirizzo": "LS", "cdc": ["1A", "4B"]},
    "GRASSI Valentina": {"materia": "Italiano e Storia", "indirizzo": "ITE", "cdc": ["1b", "2b", "3e"]},
    "GUARNIERI Oriana": {"materia": "Inglese", "indirizzo": "ITE", "cdc": ["1b", "2b", "1H"]},
    "IRACI Paola": {"materia": "Inglese", "indirizzo": "ITE", "cdc": ["1a", "2a", "3a", "4a", "5a", "3e"]},
    "LO RUSSO Libero": {"materia": "Matematica", "indirizzo": "ITE", "cdc": ["1a", "2a", "2c", "4c", "5c"]},
    "LOCATELLI Beatrice": {"materia": "Matematica", "indirizzo": "ITE", "cdc": ["3a", "3b", "4b", "5b", "3d", "3e"]},
    "LOCATELLI Ombretta": {"materia": "Matematica e Fisica", "indirizzo": "LS", "cdc": ["4A", "5A", "5D"]},
    "MANGIA Sylvie": {"materia": "Filosofia e Storia", "indirizzo": "LSU", "cdc": ["4D", "5D", "3E"]},
    "MANGIONE": {"materia": "Italiano e Geostoria", "indirizzo": "LSU", "cdc": ["1A", "1D", "2D"]},
    "MAPELLI Mario": {"materia": "Filosofia e Sc. Umane", "indirizzo": "LSU", "cdc": ["3D", "5D"]},
    "MARAFIOTI Giulia Francesca": {"materia": "Religione (IRC)", "indirizzo": "LS", "cdc": ["1A", "2A", "3A", "4A", "5A", "1B", "2B", "3B", "4B", "5B", "1D", "2D", "3D", "4D", "5D", "2F", "3F", "4F"]},
    "MARINELLI": {"materia": "Scienze Naturali", "indirizzo": "LSU", "cdc": ["1F", "1H"]},
    "MASNATA Cinzia": {"materia": "Inglese", "indirizzo": "ITE", "cdc": ["3b", "4b", "5b"]},
    "MASTROIANNI Antonella": {"materia": "Italiano e Latino", "indirizzo": "LSU", "cdc": ["3D", "5D"]},
    "OFFICIO Maela": {"materia": "Francese", "indirizzo": "ITE", "cdc": ["2a", "3a", "4a", "5a", "3e"]},
    "PELIZZONI Luisa": {"materia": "Italiano e Latino", "indirizzo": "LS", "cdc": ["2A", "4A"]},
    "PEZZOTTA Riccardo": {"materia": "Scienze Motorie", "indirizzo": "LSU", "cdc": ["2B", "1E", "2E", "1F", "4F", "5F", "1H", "2H", "3H"]},
    "PICCOLO Simona": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["1b", "1c"]},
    "PISSAVINO Anna Livia": {"materia": "Scienze Naturali", "indirizzo": "LSU", "cdc": ["2a", "2E", "3E", "2F", "3F", "4F", "5F", "2H"]},
    "POCCHIA Maria Grazia": {"materia": "Inglese", "indirizzo": "LS", "cdc": ["1A", "2A", "3A", "4A", "5A", "3H"]},
    "POVERO Dora": {"materia": "Spagnolo", "indirizzo": "ITE", "cdc": ["4a", "5a", "2c", "3d", "3e"]},
    "PRIMO Antonella": {"materia": "Scienze Naturali", "indirizzo": "LS", "cdc": ["1B", "2B", "3B", "4B", "5B", "1E"]},
    "PUTIGNANO Ilaria": {"materia": "Religione (IRC)", "indirizzo": "ITE", "cdc": ["1a", "2a", "3a", "4a", "5a", "1b", "2b", "3b", "4b", "5b", "1c", "2c", "3c", "4c", "5c", "3d", "3e", "1F"]},
    "RICUCCI Rita": {"materia": "Religione (IRC)", "indirizzo": "LSU", "cdc": ["1E", "2E", "3E", "5F", "1H", "2H", "3H", "4H"]},
    "ROSTI Enrica": {"materia": "Matematica", "indirizzo": "LS", "cdc": ["1A", "2A", "2B", "2D"]},
    "SALINA Paola": {"materia": "Matematica e Fisica", "indirizzo": "LS", "cdc": ["3B", "4B", "5B"]},
    "SALVATI Salvatore": {"materia": "Matematica", "indirizzo": "ITE", "cdc": ["4a", "5a", "2b", "3c"]},
    "SCAFURI Anna": {"materia": "Italiano e Storia", "indirizzo": "ITE", "cdc": ["1a", "2a", "3d"]},
    "SCIARRABBA Giuseppe": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["2a", "4a", "3c", "3e"]},
    "SCIORIO": {"materia": "Diritto ed Economia", "indirizzo": "LSU", "cdc": ["1D", "2D", "1E", "2E"]},
    "SERIOLI Romana Carolina": {"materia": "Disegno e Arte", "indirizzo": "LS", "cdc": ["1A", "2A", "3A", "4A", "5A", "1B", "3B", "4B", "5B"]},
    "SEVERINO Oriana": {"materia": "Spagnolo", "indirizzo": "ITE", "cdc": ["3b", "4b", "5b"]},
    "SPADARO Nunziata": {"materia": "Italiano e Latino", "indirizzo": "LS", "cdc": ["3A", "1E", "2E"]},
    "SUFFANTI": {"materia": "Filosofia e Storia", "indirizzo": "LSU", "cdc": ["3H"]},
    "SUPPL CURTI Giada": {"materia": "Francese", "indirizzo": "ITE", "cdc": ["1a", "3c", "3d"]},
    "SUPPLENTE DI BONDESAN": {"materia": "Italiano e Latino", "indirizzo": "LSU", "cdc": ["2D", "3E", "4H"]},
    "SUPPLENTE DI CECCON": {"materia": "Matematica e Fisica", "indirizzo": "LSU", "cdc": ["1b", "2B", "3E", "3F", "4F"]},
    "SUPPLENTE DI PICCARDO": {"materia": "Italiano e Latino", "indirizzo": "LSU", "cdc": ["2E", "2F", "4F"]},
    "SUPPLENTE X": {"materia": "Italiano e Latino", "indirizzo": "LSU", "cdc": ["2B", "1F", "3F", "1H"]},
    "TAMAROZZI Patrizia": {"materia": "Italiano e Storia", "indirizzo": "ITE", "cdc": ["3a", "4a", "5a"]},
    "TAVASCI Elisa": {"materia": "Economia Aziendale", "indirizzo": "ITE", "cdc": ["4c", "5c"]},
    "TORNUSCIOLO Emmanuele": {"materia": "Italiano e Geostoria", "indirizzo": "LS", "cdc": ["1B", "2B", "4D", "5F"]},
    "TRIGGIANI Fiammetta": {"materia": "Latino e Geostoria", "indirizzo": "LS", "cdc": ["2B", "2H"]},
    "TRIPODO Letteria": {"materia": "Disegno e Arte", "indirizzo": "LS", "cdc": ["2B"]},
    "VERDELLI Federica": {"materia": "Scienze Umane", "indirizzo": "LSU", "cdc": ["1H", "2H", "3H", "5F"]},
    "VILLELLA Vincenzo": {"materia": "Matematica e Fisica", "indirizzo": "LS", "cdc": ["1A", "3A", "1B", "5B", "5F"]},
    "VIOLA Maura": {"materia": "Scienze Umane", "indirizzo": "LSU", "cdc": ["1D", "2D", "4D", "4H"]},
    "VIVIANI Thomas": {"materia": "Italiano e Latino", "indirizzo": "LS", "cdc": ["5A", "3B", "1H"]},
    "VOLPE Renzo": {"materia": "Matematica e Fisica", "indirizzo": "LS", "cdc": ["2A", "3D", "4D", "3H", "4H"]}
}

# Orario Settimanale reale estratto dal Tabellone (File 1.pdf / File 6.pdf)
# Struttura: Docente -> Giorno -> Ora (1-7) -> Stato ('5B', 'DISP', 'LIBERO', ecc.)
# Ore DISP reali istituzionali: ACCIAVATTI (Lun 4a, Mar 5a), BONO (Lun 2a, Lun 6a), CACCIUOTTOLO (Gio 6a), 
# DI NUNNO (Lun 7a), FEDELI (Lun 2a, Lun 5a, Lun 6a, Mar 4a, Mer 4a, Mer 5a, Mer 7a, Gio 5a, Gio 6a, Ven 4a, Ven 5a, Ven 6a),
# GIANNUZZO (Lun 5a, Ven 5a), SUFFANTI (Lun 2a, Lun 4a, Lun 6a, Mer 2a), VERDELLI (Mar 7a).

SCHEDULE_DB = {
    "ACCIAVATTI Luciana": {
        "Lunedì": ["5B", "4B", "3B", "DISP", "5B", "LIBERO", "LIBERO"],
        "Martedì": ["4H", "4H", "5B", "4B", "DISP", "LIBERO", "LIBERO"],
        "Mercoledì": ["4B", "3B", "5B", "3B", "5B", "LIBERO", "LIBERO"],
        "Giovedì": ["LIBERO", "3B", "4B", "4B", "3B", "LIBERO", "LIBERO"],
        "Venerdì": ["LIBERO", "LIBERO", "4H", "4B", "3B", "LIBERO", "LIBERO"]
    },
    "BONO Lamberto": {
        "Lunedì": ["3a", "DISP", "3a", "1a", "5a", "DISP", "LIBERO"],
        "Martedì": ["5a", "5a", "3a", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Mercoledì": ["5a", "5a", "3a", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Giovedì": ["5a", "5a", "3a", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["3a", "5a", "1a", "LIBERO", "LIBERO", "LIBERO", "LIBERO"]
    },
    "CACCIUOTTOLO Adalgisa": {
        "Lunedì": ["3A", "4F", "4F", "3F", "3A", "LIBERO", "LIBERO"],
        "Martedì": ["3F", "5F", "5F", "4F", "3A", "LIBERO", "LIBERO"],
        "Mercoledì": ["3F", "4F", "3A", "3F", "4F", "LIBERO", "LIBERO"],
        "Giovedì": ["LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "DISP", "LIBERO"],
        "Venerdì": ["3A", "3F", "4F", "LIBERO", "LIBERO", "LIBERO", "LIBERO"]
    },
    "FEDELI Angelo": {
        "Lunedì": ["3d", "DISP", "3d", "2c", "DISP", "DISP", "LIBERO"],
        "Martedì": ["3d", "2b", "3d", "DISP", "LIBERO", "LIBERO", "LIBERO"],
        "Mercoledì": ["LIBERO", "DISP", "2c", "3d", "DISP", "LIBERO", "DISP"],
        "Giovedì": ["2b", "DISP", "DISP", "3d", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["LIBERO", "LIBERO", "DISP", "DISP", "DISP", "LIBERO", "LIBERO"]
    },
    "GIANNUZZO Nadia": {
        "Lunedì": ["5b", "5b", "3b", "4b", "DISP", "LIBERO", "LIBERO"],
        "Martedì": ["5b", "4b", "5b", "3b", "LIBERO", "LIBERO", "LIBERO"],
        "Mercoledì": ["5b", "4b", "3b", "3b", "LIBERO", "LIBERO", "LIBERO"],
        "Giovedì": ["3b", "LIBERO", "4b", "4b", "5b", "LIBERO", "LIBERO"],
        "Venerdì": ["LIBERO", "LIBERO", "LIBERO", "LIBERO", "DISP", "LIBERO", "LIBERO"]
    },
    "SUFFANTI": {
        "Lunedì": ["3H", "DISP", "3H", "DISP", "3H", "DISP", "LIBERO"],
        "Martedì": ["3H", "DISP", "3H", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Mercoledì": ["LIBERO", "DISP", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Giovedì": ["3H", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["3H", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"]
    },
    "VERDELLI Federica": {
        "Lunedì": ["2H", "3H", "1H", "5F", "2H", "5F", "LIBERO"],
        "Martedì": ["DISP", "2H", "1H", "3H", "5F", "5F", "3H"],
        "Mercoledì": ["5F", "2H", "1H", "3H", "1H", "3H", "LIBERO"],
        "Giovedì": ["LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["1H", "2H", "3H", "5F", "LIBERO", "LIBERO", "LIBERO"]
    },
    "BARRACO Maria Laura": {
        "Lunedì": ["1B", "5B", "5B", "2F", "1B", "5B", "LIBERO"],
        "Martedì": ["5B", "5B", "5B", "1B", "1B", "2F", "LIBERO"],
        "Mercoledì": ["2F", "1B", "2F", "5B", "1B", "1B", "LIBERO"],
        "Giovedì": ["1B", "5B", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["5B", "1B", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"]
    },
    "COMINI Fabio": {
        "Lunedì": ["4A", "4A", "4D", "5A", "5A", "LIBERO", "LIBERO"],
        "Martedì": ["5A", "4D", "4A", "5A", "3D", "LIBERO", "LIBERO"],
        "Mercoledì": ["4A", "5A", "3D", "4A", "5A", "LIBERO", "LIBERO"],
        "Giovedì": ["LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["4A", "5A", "3D", "4D", "LIBERO", "LIBERO", "LIBERO"]
    },
    "DE CASTRO Calogero": {
        "Lunedì": ["5A", "1B", "5B", "3B", "2A", "LIBERO", "LIBERO"],
        "Martedì": ["4B", "5A", "1B", "3A", "1A", "LIBERO", "LIBERO"],
        "Mercoledì": ["4A", "4A", "2A", "3B", "4B", "LIBERO", "LIBERO"],
        "Giovedì": ["3A", "5B", "1A", "LIBERO", "LIBERO", "LIBERO", "LIBERO"],
        "Venerdì": ["LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO", "LIBERO"]
    }
}

# Popoliamo orari standard di default per tutti i restanti 94 docenti
for doc, info in DOCENTI_DB.items():
    if doc not in SCHEDULE_DB:
        # Assegniamo le ore di lezione in base alle loro classi CdC
        schedule_doc = {"Lunedì": ["LIBERO"]*7, "Martedì": ["LIBERO"]*7, "Mercoledì": ["LIBERO"]*7, "Giovedì": ["LIBERO"]*7, "Venerdì": ["LIBERO"]*7}
        # Inseriamo supplenza/lezione demo o DISP
        for i, cls in enumerate(info["cdc"]):
            g = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì"][i % 5]
            h = (i * 2) % 6
            schedule_doc[g][h] = cls
            # Se ha meno di 18 ore ed è idoneo, lasciamo un'ora DISP
            if i == 0 and len(info["cdc"]) > 2:
                schedule_doc[g][(h+1)%6] = "DISP"
        SCHEDULE_DB[doc] = schedule_doc

# Inizializzazione Registro Sostituzioni in Session State
if 'registro' not in st.session_state:
    st.session_state.registro = []

# Sidebar di Inserimento Assenza
st.sidebar.header("📋 Segnalazione Docente Assente")

docenti_list = sorted(list(DOCENTI_DB.keys()))
docente_assente = st.sidebar.selectbox("Docente Assente", docenti_list, index=0)
giorno = st.sidebar.selectbox("Giorno della Settimana", ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì'])
ora_idx = st.sidebar.selectbox("Ora di Lezione", ['1ª ora (8:00)', '2ª ora (8:55)', '3ª ora (10:00)', '4ª ora (10:55)', '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)'])
h_num = int(ora_idx.split('ª')[0]) - 1

# Individuiamo la classe prevista nell'orario del docente assente
lezione_prevista = SCHEDULE_DB[docente_assente][giorno][h_num]

st.sidebar.markdown("---")
st.sidebar.info(f"**Materia**: {DOCENTI_DB[docente_assente]['materia']}\n\n**Stato Orario Docente Assente**: `{lezione_prevista}`")

if lezione_prevista in ['LIBERO', 'DISP']:
    st.warning(f"⚠️ Il docente **{docente_assente}** risulta in stato `{lezione_prevista}` il **{giorno}** alla **{ora_idx}**. Non sembra essere di lezione in una classe.")
    classe_target = st.sidebar.selectbox("Seleziona manualmente la classe da coprire:", list(CLASSES_INFO.keys()))
else:
    classe_target = lezione_prevista

indirizzo_target = CLASSES_INFO.get(classe_target, 'LS')
materia_target = DOCENTI_DB[docente_assente]['materia']

# Tasto di ricerca algoritmo a cascata
st.markdown(f"### Ricerca Sostituto per **{docente_assente}** — {giorno}, {ora_idx}")
st.markdown(f"📍 **Classe interessata**: `{classe_target}` ({indirizzo_target}) | 📘 **Materia**: `{materia_target}`")

# Algoritmo a Cascata
candidati_p1 = []  # DISP nello stesso CdC
candidati_p2a = [] # DISP stesso Indirizzo + stessa materia
candidati_p2b = [] # DISP stesso Indirizzo + altra materia
candidati_p3a = [] # DISP altro Indirizzo + stessa materia
candidati_p3b = [] # DISP altro Indirizzo + altra materia
candidati_p4 = []  # Ora buca / extra

for doc, sch in SCHEDULE_DB.items():
    if doc == docente_assente:
        continue
    
    st_ora = sch[giorno][h_num]
    materia_doc = DOCENTI_DB[doc]['materia']
    ind_doc = DOCENTI_DB[doc]['indirizzo']
    cdc_doc = DOCENTI_DB[doc]['cdc']
    
    # Conteggio sostituzioni già fatte nell'anno
    sost_disp = sum(1 for r in st.session_state.registro if r['Sostituto'] == doc and 'DISP' in r['Tipo'])
    sost_extra = sum(1 for r in st.session_state.registro if r['Sostituto'] == doc and 'EXTRA' in r['Tipo'])

    if st_ora == 'DISP':
        is_same_cdc = classe_target in cdc_doc
        is_same_ind = ind_doc == indirizzo_target
        is_same_mat = materia_doc == materia_target
        
        c_info = {
            'Docente': doc, 'Materia': materia_doc, 'Indirizzo': ind_doc, 
            'CdC': 'SÌ' if is_same_cdc else 'No', 'DISP_Anno': sost_disp, 'EXTRA_Anno': sost_extra
        }
        
        if is_same_cdc:
            candidati_p1.append(c_info)
        elif is_same_ind and is_same_mat:
            candidati_p2a.append(c_info)
        elif is_same_ind:
            candidati_p2b.append(c_info)
        elif is_same_mat:
            candidati_p3a.append(c_info)
        else:
            candidati_p3b.append(c_info)
            
    elif st_ora == 'LIBERO':
        # Verifica se è ora buca (ha lezione prima e dopo)
        h_prev = sch[giorno][h_num - 1] if h_num > 0 else 'LIBERO'
        h_next = sch[giorno][h_num + 1] if h_num < 6 else 'LIBERO'
        
        if h_prev not in ['LIBERO', 'DISP'] and h_next not in ['LIBERO', 'DISP']:
            tipo_buca = "Ora Buca (Presente a scuola)"
        elif h_prev not in ['LIBERO', 'DISP']:
            tipo_buca = "Uscita Posticipata (+1 ora)"
        elif h_next not in ['LIBERO', 'DISP']:
            tipo_buca = "Entrata Anticipata (+1 ora)"
        else:
            tipo_buca = None
            
        if tipo_buca:
            candidati_p4.append({
                'Docente': doc, 'Materia': materia_doc, 'Indirizzo': ind_doc,
                'Stato': tipo_buca, 'CdC': 'SÌ' if classe_target in cdc_doc else 'No',
                'DISP_Anno': sost_disp, 'EXTRA_Anno': sost_extra
            })

# Visualizzazione Risultati per Livello di Priorità
st.markdown("---")

sostituto_scelto = None
tipo_sostituzione = None

if candidati_p1:
    st.success("🟢 **PRIORITÀ 1: Docente a Disposizione nello Stesso Consiglio di Classe (CdC)**")
    df_p1 = pd.DataFrame(candidati_p1)
    st.dataframe(df_p1, use_container_width=True)
    sostituto_scelto = candidati_p1[0]['Docente']
    tipo_sostituzione = "DISP (In Orario - Stesso CdC)"
    
elif candidati_p2a or candidati_p2b:
    st.info("🔵 **PRIORITÀ 2: Docente a Disposizione dello Stesso Indirizzo**")
    if candidati_p2a:
        st.write("👉 *Stessa Materia:*")
        st.dataframe(pd.DataFrame(candidati_p2a), use_container_width=True)
        sostituto_scelto = candidati_p2a[0]['Docente']
    else:
        st.write("👉 *Altra Materia:*")
        st.dataframe(pd.DataFrame(candidati_p2b), use_container_width=True)
        sostituto_scelto = candidati_p2b[0]['Docente']
    tipo_sostituzione = "DISP (In Orario - Stesso Indirizzo)"

elif candidati_p3a or candidati_p3b:
    st.warning("🟡 **PRIORITÀ 3: Docente a Disposizione di un Altro Indirizzo**")
    if candidati_p3a:
        st.write("👉 *Stessa Materia:*")
        st.dataframe(pd.DataFrame(candidati_p3a), use_container_width=True)
        sostituto_scelto = candidati_p3a[0]['Docente']
    else:
        st.write("👉 *Altra Materia:*")
        st.dataframe(pd.DataFrame(candidati_p3b), use_container_width=True)
        sostituto_scelto = candidati_p3b[0]['Docente']
    tipo_sostituzione = "DISP (In Orario - Altro Indirizzo)"

else:
    st.error("🔴 **Nessun docente con ora a disposizione libero. Attivazione PRIORITÀ 4 (Ore Buche / Straordinario)**")
    if candidati_p4:
        st.markdown("**Elenco Docenti per Contatto Separato (Ora Buca / Entrata Anticipata / Uscita Posticipata):**")
        df_p4 = pd.DataFrame(candidati_p4)
        st.dataframe(df_p4, use_container_width=True)
        sostituto_scelto = candidati_p4[0]['Docente']
        tipo_sostituzione = f"EXTRA ({candidati_p4[0]['Stato']})"
    else:
        st.write("Nessun docente disponibile neanche fuori orario.")

# Conferma Sostituzione
if sostituto_scelto:
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"Candidato consigliato: **{sostituto_scelto}** (`{tipo_sostituzione}`)")
    with col2:
        if st.button("✅ Conferma Assegnazione e Registra", type="primary"):
            st.session_state.registro.append({
                'Data/Giorno': giorno,
                'Ora': ora_idx,
                'Classe': classe_target,
                'Docente Assente': docente_assente,
                'Sostituto': sostituto_scelto,
                'Tipo': tipo_sostituzione
            })
            st.success(f"Sostituzione registrata per {sostituto_scelto}!")

# Registro Annuale e Totali
st.markdown("---")
st.subheader("📈 Registro Annuale Sostituzioni e Tracciamento Ore")

if st.session_state.registro:
    df_reg = pd.DataFrame(st.session_state.registro)
    st.dataframe(df_reg, use_container_width=True)
    
    # Grafico riassuntivo
    chart_data = df_reg.groupby(['Sostituto', 'Tipo']).size().unstack(fill_value=0)
    st.bar_chart(chart_data)
else:
    st.info("Il registro annuale è vuoto. Le sostituzioni confermate appariranno qui ed aggiorneranno il conteggio ore dei docenti.")
