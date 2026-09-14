import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Gestione Sostituzioni - I.I.S. Italo Calvino", page_icon="🏫", layout="wide")

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

# Indirizzi dell'Istituto
CLASSES_INFO = {
    '1A': ('LS', 'Liceo Scientifico'), '2A': ('LS', 'Liceo Scientifico'), '3A': ('LS', 'Liceo Scientifico'), '4A': ('LS', 'Liceo Scientifico'), '5A': ('LS', 'Liceo Scientifico'),
    '1B': ('LS', 'Liceo Scientifico'), '2B': ('LS', 'Liceo Scientifico'), '3B': ('LS', 'Liceo Scientifico'), '4B': ('LS', 'Liceo Scientifico'), '5B': ('LS', 'Liceo Scientifico'),
    '1D': ('LSU', 'Liceo Scienze Umane'), '2D': ('LSU', 'Liceo Scienze Umane'), '3D': ('LSU', 'Liceo Scienze Umane'), '4D': ('LSU', 'Liceo Scienze Umane'), '5D': ('LSU', 'Liceo Scienze Umane'),
    '1E': ('LSU', 'Liceo Scienze Umane'), '2E': ('LSU', 'Liceo Scienze Umane'), '3E': ('LSU', 'Liceo Scienze Umane'), 
    '1F': ('LSU', 'Liceo Scienze Umane'), '2F': ('LSU', 'Liceo Scienze Umane'), '3F': ('LSU', 'Liceo Scienze Umane'), '4F': ('LSU', 'Liceo Scienze Umane'), '5F': ('LSU', 'Liceo Scienze Umane'),
    '1H': ('LSU', 'Liceo Scienze Umane'), '2H': ('LSU', 'Liceo Scienze Umane'), '3H': ('LSU', 'Liceo Scienze Umane'), '4H': ('LSU', 'Liceo Scienze Umane'),
    '1a': ('ITE', 'Istituto Tecnico Economico'), '2a': ('ITE', 'Istituto Tecnico Economico'), '3a': ('ITE', 'Istituto Tecnico Economico'), '4a': ('ITE', 'Istituto Tecnico Economico'), '5a': ('ITE', 'Istituto Tecnico Economico'),
    '1b': ('ITE', 'Istituto Tecnico Economico'), '2b': ('ITE', 'Istituto Tecnico Economico'), '3b': ('ITE', 'Istituto Tecnico Economico'), '4b': ('ITE', 'Istituto Tecnico Economico'), '5b': ('ITE', 'Istituto Tecnico Economico'),
    '1c': ('ITE', 'Istituto Tecnico Economico'), '2c': ('ITE', 'Istituto Tecnico Economico'), '3c': ('ITE', 'Istituto Tecnico Economico'), '4c': ('ITE', 'Istituto Tecnico Economico'), '5c': ('ITE', 'Istituto Tecnico Economico'),
    '3d': ('ITE', 'Istituto Tecnico Economico'), '3e': ('ITE', 'Istituto Tecnico Economico')
}

GIORNI = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']
ORE = ['1ª ora (08:00)', '2ª ora (08:55)', '3ª ora (10:00)', '4ª ora (10:55)', '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)']

# Inizializzazione Registro Sostituzioni
if 'registro' not in st.session_state:
    st.session_state.registro = []

# Sidebar - Caricamento Orario Excel/CSV
st.sidebar.header("📁 Caricamento Orario Scolastico")
uploaded_file = st.sidebar.file_uploader("Carica File Orario (Excel / CSV)", type=['xlsx', 'csv'])

st.sidebar.markdown("---")
st.sidebar.header("📋 Segnalazione Docente Assente")

# Esempio dati base predefiniti se non viene caricato un file esterno
default_teachers_data = [
    {
        'Docente': 'ACCIAVATTI Luciana', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '3B, 4B, 5B, 4H',
        'Lunedì_1ª ora (08:00)': '5B', 'Lunedì_2ª ora (08:55)': '4B', 'Lunedì_3ª ora (10:00)': '3B', 'Lunedì_4ª ora (10:55)': 'DISP', 'Lunedì_5ª ora (12:00)': '5B', 'Lunedì_6ª ora (12:55)': '4H', 'Lunedì_7ª ora (14:00)': '4H',
        'Martedì_1ª ora (08:00)': '5B', 'Martedì_2ª ora (08:55)': '4B', 'Martedì_3ª ora (10:00)': '4B', 'Martedì_4ª ora (10:55)': '3B', 'Martedì_5ª ora (12:00)': '5B', 'Martedì_6ª ora (12:55)': '', 'Martedì_7ª ora (14:00)': '',
        'Mercoledì_1ª ora (08:00)': '3B', 'Mercoledì_2ª ora (08:55)': '5B', 'Mercoledì_3ª ora (10:00)': '3B', 'Mercoledì_4ª ora (10:55)': '4B', 'Mercoledì_5ª ora (12:00)': '4B', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '3B', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'BARRACO Maria Laura', 'Materia': 'Italiano e Latino', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '1B, 2F, 5B',
        'Lunedì_1ª ora (08:00)': 'DISP', 'Lunedì_2ª ora (08:55)': '1B', 'Lunedì_3ª ora (10:00)': '5B', 'Lunedì_4ª ora (10:55)': '5B', 'Lunedì_5ª ora (12:00)': '2F', 'Lunedì_6ª ora (12:55)': '1B', 'Lunedì_7ª ora (14:00)': '5B',
        'Martedì_1ª ora (08:00)': '5B', 'Martedì_2ª ora (08:55)': '5B', 'Martedì_3ª ora (10:00)': '5B', 'Martedì_4ª ora (10:55)': '1B', 'Martedì_5ª ora (12:00)': '1B', 'Martedì_6ª ora (12:55)': '2F', 'Martedì_7ª ora (14:00)': '2F',
        'Mercoledì_1ª ora (08:00)': '1B', 'Mercoledì_2ª ora (08:55)': '2F', 'Mercoledì_3ª ora (10:00)': '5B', 'Mercoledì_4ª ora (10:55)': '1B', 'Mercoledì_5ª ora (12:00)': '1B', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'BELLETTI Susanna', 'Materia': 'Scienze Motorie', 'Indirizzo': 'ITE',
        'CdC': '1b, 2b, 3b, 4b, 5b, 3c, 4c, 5c, 3e',
        'Lunedì_1ª ora (08:00)': '', 'Lunedì_2ª ora (08:55)': '', 'Lunedì_3ª ora (10:00)': '', 'Lunedì_4ª ora (10:55)': '', 'Lunedì_5ª ora (12:00)': '2b', 'Lunedì_6ª ora (12:55)': '4b', 'Lunedì_7ª ora (14:00)': '3c',
        'Martedì_1ª ora (08:00)': '', 'Martedì_2ª ora (08:55)': '', 'Martedì_3ª ora (10:00)': '5c', 'Martedì_4ª ora (10:55)': '2b', 'Martedì_5ª ora (12:00)': '5b', 'Martedì_6ª ora (12:55)': '3b', 'Martedì_7ª ora (14:00)': '1b',
        'Mercoledì_1ª ora (08:00)': '3e', 'Mercoledì_2ª ora (08:55)': '3e', 'Mercoledì_3ª ora (10:00)': '5c', 'Mercoledì_4ª ora (10:55)': '4b', 'Mercoledì_5ª ora (12:00)': '', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '3b', 'Giovedì_4ª ora (10:55)': '4c', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '1b', 'Venerdì_6ª ora (12:55)': '5b', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'BONO Lamberto', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE',
        'CdC': '1a, 3a, 5a',
        'Lunedì_1ª ora (08:00)': '3a', 'Lunedì_2ª ora (08:55)': 'DISP', 'Lunedì_3ª ora (10:00)': '3a', 'Lunedì_4ª ora (10:55)': '1a', 'Lunedì_5ª ora (12:00)': '5a', 'Lunedì_6ª ora (12:55)': 'DISP', 'Lunedì_7ª ora (14:00)': '5a',
        'Martedì_1ª ora (08:00)': '5a', 'Martedì_2ª ora (08:55)': '3a', 'Martedì_3ª ora (10:00)': '5a', 'Martedì_4ª ora (10:55)': '5a', 'Martedì_5ª ora (12:00)': '3a', 'Martedì_6ª ora (12:55)': '3a', 'Martedì_7ª ora (14:00)': '5a',
        'Mercoledì_1ª ora (08:00)': '5a', 'Mercoledì_2ª ora (08:55)': '3a', 'Mercoledì_3ª ora (10:00)': '3a', 'Mercoledì_4ª ora (10:55)': '5a', 'Mercoledì_5ª ora (12:00)': '1a', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'SALVATI Salvatore', 'Materia': 'Matematica ITE', 'Indirizzo': 'ITE',
        'CdC': '4a, 3c, 5a, 2b, 5b',
        'Lunedì_1ª ora (08:00)': '4a', 'Lunedì_2ª ora (08:55)': '3c', 'Lunedì_3ª ora (10:00)': '5a', 'Lunedì_4ª ora (10:55)': '3c', 'Lunedì_5ª ora (12:00)': '2b', 'Lunedì_6ª ora (12:55)': '4a', 'Lunedì_7ª ora (14:00)': '2b',
        'Martedì_1ª ora (08:00)': '4a', 'Martedì_2ª ora (08:55)': '5a', 'Martedì_3ª ora (10:00)': '5a', 'Martedì_4ª ora (10:55)': '2b', 'Martedì_5ª ora (12:00)': '', 'Martedì_6ª ora (12:55)': '3c', 'Martedì_7ª ora (14:00)': '2b',
        'Mercoledì_1ª ora (08:00)': '', 'Mercoledì_2ª ora (08:55)': '', 'Mercoledì_3ª ora (10:00)': '', 'Mercoledì_4ª ora (10:55)': '', 'Mercoledì_5ª ora (12:00)': '', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'FEDELI Angelo', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE',
        'CdC': '2b, 2c, 3d',
        'Lunedì_1ª ora (08:00)': '3d', 'Lunedì_2ª ora (08:55)': 'DISP', 'Lunedì_3ª ora (10:00)': '3d', 'Lunedì_4ª ora (10:55)': '2c', 'Lunedì_5ª ora (12:00)': 'DISP', 'Lunedì_6ª ora (12:55)': 'DISP', 'Lunedì_7ª ora (14:00)': '3d',
        'Martedì_1ª ora (08:00)': '2b', 'Martedì_2ª ora (08:55)': '3d', 'Martedì_3ª ora (10:00)': 'DISP', 'Martedì_4ª ora (10:55)': 'DISP', 'Martedì_5ª ora (12:00)': '2c', 'Martedì_6ª ora (12:55)': '3d', 'Martedì_7ª ora (14:00)': 'DISP',
        'Mercoledì_1ª ora (08:00)': '', 'Mercoledì_2ª ora (08:55)': '', 'Mercoledì_3ª ora (10:00)': '', 'Mercoledì_4ª ora (10:55)': '', 'Mercoledì_5ª ora (12:00)': '', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    },
    {
        'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '4A, 5A, 3D, 4D',
        'Lunedì_1ª ora (08:00)': '4A', 'Lunedì_2ª ora (08:55)': '4A', 'Lunedì_3ª ora (10:00)': '4D', 'Lunedì_4ª ora (10:55)': '5A', 'Lunedì_5ª ora (12:00)': '5A', 'Lunedì_6ª ora (12:55)': '5A', 'Lunedì_7ª ora (14:00)': '4D',
        'Martedì_1ª ora (08:00)': '4A', 'Martedì_2ª ora (08:55)': '5A', 'Martedì_3ª ora (10:00)': '3D', 'Martedì_4ª ora (10:55)': 'DISP', 'Martedì_5ª ora (12:00)': '4A', 'Martedì_6ª ora (12:55)': '3D', 'Martedì_7ª ora (14:00)': '4A',
        'Mercoledì_1ª ora (08:00)': '', 'Mercoledì_2ª ora (08:55)': '', 'Mercoledì_3ª ora (10:00)': '', 'Mercoledì_4ª ora (10:55)': '', 'Mercoledì_5ª ora (12:00)': '', 'Mercoledì_6ª ora (12:55)': '', 'Mercoledì_7ª ora (14:00)': '',
        'Giovedì_1ª ora (08:00)': '', 'Giovedì_2ª ora (08:55)': '', 'Giovedì_3ª ora (10:00)': '', 'Giovedì_4ª ora (10:55)': '', 'Giovedì_5ª ora (12:00)': '', 'Giovedì_6ª ora (12:55)': '', 'Giovedì_7ª ora (14:00)': '',
        'Venerdì_1ª ora (08:00)': '', 'Venerdì_2ª ora (08:55)': '', 'Venerdì_3ª ora (10:00)': '', 'Venerdì_4ª ora (10:55)': '', 'Venerdì_5ª ora (12:00)': '', 'Venerdì_6ª ora (12:55)': '', 'Venerdì_7ª ora (14:00)': ''
    }
]

# Caricamento del dataset (da file caricato o default)
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_schedule = pd.read_csv(uploaded_file)
        else:
            df_schedule = pd.read_excel(uploaded_file)
        st.sidebar.success(f"✅ Caricato file: `{uploaded_file.name}` ({len(df_schedule)} docenti)")
    except Exception as e:
        st.sidebar.error(f"Errore nella lettura del file: {e}")
        df_schedule = pd.DataFrame(default_teachers_data)
else:
    df_schedule = pd.DataFrame(default_teachers_data)

# Selezione Form per Assenza
docente_list = sorted(df_schedule['Docente'].unique().tolist())
docente_assente = st.sidebar.selectbox("Docente Assente", docente_list, index=2 if 'BELLETTI Susanna' in docente_list else 0)
giorno = st.sidebar.selectbox("Giorno della Settimana", GIORNI, index=1)
ora = st.sidebar.selectbox("Ora di Lezione", ORE, index=4)

# Lettura dati docente assente
row_doc = df_schedule[df_schedule['Docente'] == docente_assente].iloc[0]
slot_key = f"{giorno}_{ora}"
classe_rilevata = str(row_doc.get(slot_key, '')).strip()

st.sidebar.markdown("---")
if classe_rilevata and classe_rilevata.upper() != 'DISP' and classe_rilevata != 'nan' and classe_rilevata != '':
    st.sidebar.success(f"📍 **Classe rilevata automaticamente:** {classe_rilevata}")
    classe_effettiva = classe_rilevata
else:
    if classe_rilevata.upper() == 'DISP':
        st.sidebar.info(f"ℹ️ {docente_assente} era in ore a DISPOSIZIONE ({ora}).")
    else:
        st.sidebar.warning(f"⚠️ Nessuna classe in orario trovata per {docente_assente} il {giorno} alla {ora}.")
    classe_effettiva = st.sidebar.selectbox("Seleziona manualmente la classe da coprire:", list(CLASSES_INFO.keys()), index=9)

materia_docente = row_doc.get('Materia', 'Generale')
indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_effettiva, ('ITE', 'Istituto Tecnico Economico'))

st.markdown(f"## Ricerca Sostituto per **{docente_assente}** — {giorno}, {ora}")
st.info(f"📍 **Classe interessata:** `{classe_effettiva}` ({indirizzo_nome}) | 📚 **Materia da coprire:** `{materia_docente}`")

# Algoritmo di Ricerca Sostituti in tempo reale dal DataFrame
candidati_disp = []
candidati_extra = []

for idx, r in df_schedule.iterrows():
    d_nome = r['Docente']
    if d_nome == docente_assente:
        continue
    
    d_mat = r.get('Materia', '')
    d_ind = r.get('Indirizzo', '')
    d_cdc_list = [c.strip() for c in str(r.get('CdC', '')).split(',') if c.strip()]
    
    is_cdc = classe_effettiva in d_cdc_list
    is_ind = (d_ind == indirizzo_codice)
    is_mat = (d_mat == materia_docente)
    
    val_ora = str(r.get(slot_key, '')).strip()
    
    # 1. Caso DISP
    if val_ora.upper() == 'DISP':
        if is_cdc:
            prio = "Priorità 1 (Stesso CdC)"
        elif is_ind and is_mat:
            prio = "Priorità 2a (Stesso Indirizzo / Stessa Materia)"
        elif is_ind:
            prio = "Priorità 2b (Stesso Indirizzo / Altra Materia)"
        elif is_mat:
            prio = "Priorità 3a (Altro Indirizzo / Stessa Materia)"
        else:
            prio = "Priorità 3b (Altro Indirizzo / Altra Materia)"
            
        candidati_disp.append({
            'Docente': d_nome,
            'Materia': d_mat,
            'Indirizzo': d_ind,
            'Stato': 'DISP (In Orario)',
            'CdC': f"Sì ({classe_effettiva})" if is_cdc else "No",
            'Priorità': prio,
            'Tipo': 'DISP'
        })
        
    # 2. Caso EXTRA / Ora Buca / Entrata / Uscita
    elif val_ora == '' or val_ora == 'nan':
        # Calcolo lezioni nel giorno
        ora_idx = ORE.index(ora)
        h_before = str(r.get(f"{giorno}_{ORE[ora_idx-1]}", '')).strip() if ora_idx > 0 else ''
        h_after = str(r.get(f"{giorno}_{ORE[ora_idx+1]}", '')).strip() if ora_idx < len(ORE)-1 else ''
        
        has_before = (h_before != '' and h_before != 'nan' and h_before.upper() != 'DISP')
        has_after = (h_after != '' and h_after != 'nan' and h_after.upper() != 'DISP')
        
        if has_before and has_after:
            tipo_extra = "Ora Buca (Lezione prima e dopo)"
        elif has_after:
            tipo_extra = "Entrata Anticipata (+1h)"
        elif has_before:
            tipo_extra = "Uscita Posticipata (+1h)"
        else:
            tipo_extra = "Libero / Fuori Servizio"
            
        if has_before or has_after:
            candidati_extra.append({
                'Docente': d_nome,
                'Materia': d_mat,
                'Indirizzo': d_ind,
                'Stato': tipo_extra,
                'CdC': f"Sì ({classe_effettiva})" if is_cdc else "No",
                'Priorità': 'Priorità 4 (Ora Buca / Extra)',
                'Tipo': 'EXTRA'
            })

# Visualizzazione Risultati
st.markdown("### 📊 Graduatoria dei Candidati Trovati")

all_candidates = candidati_disp + candidati_extra

if all_candidates:
    df_cand = pd.DataFrame(all_candidates)
    st.dataframe(df_cand, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🎯 Selezione Manuale / Conferma Sostituto")
    
    nodi_docenti = [f"{c['Docente']} | {c['Priorità']} | {c['Stato']}" for c in all_candidates]
    scelta_idx = st.selectbox("Scegli il docente da assegnare tra tutti quelli identificati:", range(len(nodi_docenti)), format_func=lambda i: nodi_docenti[i])
    
    docente_selezionato = all_candidates[scelta_idx]
    
    if st.button("✅ Conferma e Registra Sostituzione", type="primary"):
        st.session_state.registro.append({
            'Docente Sostituto': docente_selezionato['Docente'],
            'Docente Assente': docente_assente,
            'Classe': classe_effettiva,
            'Giorno': giorno,
            'Ora': ora,
            'Tipologia': docente_selezionato['Tipo'],
            'Priorità Applicata': docente_selezionato['Priorità']
        })
        st.success(f"Sostituzione registrata con successo per **{docente_selezionato['Docente']}**!")
else:
    st.warning("Nessun docente disponibile o contattabile trovato per questa ora.")

# Registro e Gestione Orario
st.markdown("---")
st.subheader("📊 Registro Annuale Sostituzioni")
if st.session_state.registro:
    df_reg = pd.DataFrame(st.session_state.registro)
    st.dataframe(df_reg, use_container_width=True)
else:
    st.info("Nessuna sostituzione registrata al momento.")
