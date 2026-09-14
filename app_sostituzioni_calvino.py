import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestione Sostituzioni - I.I.S. Italo Calvino", page_icon="🏫", layout="wide")

# Intestazione
st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

# Mappatura Indirizzi e Classi dell'Istituto
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

# Consigli di Classe 2b (ITE)
CDC_2B = [
    'GRASSI Valentina', 'SALVATI Salvatore', 'DE TURSI', 'FEDELI Angelo', 
    'CATTANEI Giuseppe', 'VACANTE 3 (Informatica)', 'ALBANESE Alessandra', 
    'BELLETTI Susanna', 'PUTIGNANO Ilaria', 'GUARNIERI Oriana', 'VACANTE 1 (Spagnolo)'
]

# Database Orario Reale e Dettagliato per Docente
TEACHER_SCHEDULES = {
    'BELLETTI Susanna': {
        'Materia': 'Scienze Motorie',
        'Indirizzo': 'ITE',
        'CdC_Classi': ['1b', '2b', '3b', '4b', '5b', '3c', '4c', '5c', '3e'],
        'Orario': {
            'Lunedì': {'5ª ora (12:00)': '2b', '6ª ora (12:55)': '4b', '7ª ora (14:00)': '3c'},
            'Martedì': {'3ª ora (10:00)': '5c', '4ª ora (10:55)': '2b', '5ª ora (12:00)': '5b', '6ª ora (12:55)': '3b', '7ª ora (14:00)': '1b'},
            'Mercoledì': {'1ª ora (08:00)': '3e', '2ª ora (08:55)': '3e', '3ª ora (10:00)': '5c', '4ª ora (10:55)': '4b'},
            'Giovedì': {'3ª ora (10:00)': '3b', '4ª ora (10:55)': '4c'},
            'Venerdì': {'5ª ora (12:00)': '1b', '6ª ora (12:55)': '5b'}
        }
    },
    'ACCIAVATTI Luciana': {
        'Materia': 'Filosofia e Storia',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['3B', '4B', '5B', '4H'],
        'Orario': {
            'Lunedì': {'1ª ora (08:00)': '5B', '2ª ora (08:55)': '4B', '3ª ora (10:00)': '3B', '4ª ora (10:55)': 'DISP', '5ª ora (12:00)': '5B', '6ª ora (12:55)': '4H', '7ª ora (14:00)': '4H'},
            'Martedì': {'1ª ora (08:00)': '5B', '2ª ora (08:55)': '4B', '3ª ora (10:00)': '4B', '4ª ora (10:55)': '3B', '5ª ora (12:00)': '5B'},
            'Mercoledì': {'1ª ora (08:00)': '3B', '2ª ora (08:55)': '5B', '3ª ora (10:00)': '3B', '4ª ora (10:55)': '4B', '5ª ora (12:00)': '4B'},
            'Giovedì': {'1ª ora (08:00)': '3B'},
            'Venerdì': {}
        }
    },
    'FEDELI Angelo': {
        'Materia': 'Economia Aziendale',
        'Indirizzo': 'ITE',
        'CdC_Classi': ['2b', '2c', '3d'],
        'Orario': {
            'Martedì': {'4ª ora (10:55)': 'DISP', '5ª ora (12:00)': 'DISP'}
        }
    },
    'BONO Lamberto': {
        'Materia': 'Economia Aziendale',
        'Indirizzo': 'ITE',
        'CdC_Classi': ['1a', '3a', '5a'],
        'Orario': {
            'Lunedì': {'2ª ora (08:55)': 'DISP', '6ª ora (12:55)': 'DISP'}
        }
    },
    'COMINI Fabio': {
        'Materia': 'Filosofia e Storia',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['4D', '4A', '5A', '3D'],
        'Orario': {
            'Martedì': {'4ª ora (10:55)': 'DISP'}
        }
    },
    'BARRACO Maria Laura': {
        'Materia': 'Italiano e Latino',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['1B', '2F', '5B'],
        'Orario': {
            'Lunedì': {'1ª ora (08:00)': 'DISP'}
        }
    }
}

# Docenti a disposizione (DISP) censiti
DISP_TEACHERS = [
    {'Docente': 'FEDELI Angelo', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['2b', '2c', '3d'], 'Giorno': 'Martedì', 'Ora': '4ª ora (10:55)', 'DISP_Anno': 1, 'EXTRA_Anno': 0},
    {'Docente': 'BONO Lamberto', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['1a', '3a', '5a'], 'Giorno': 'Lunedì', 'Ora': '2ª ora (08:55)', 'DISP_Anno': 4, 'EXTRA_Anno': 1},
    {'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['4D', '4A', '5A', '3D'], 'Giorno': 'Martedì', 'Ora': '4ª ora (10:55)', 'DISP_Anno': 5, 'EXTRA_Anno': 0},
    {'Docente': 'DE CASTRO Calogero', 'Materia': 'Scienze Motorie', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['1A', '2A', '3A', '4A', '5A', '1B', '3B', '4B', '5B'], 'Giorno': 'Martedì', 'Ora': '4ª ora (10:55)', 'DISP_Anno': 2, 'EXTRA_Anno': 2},
    {'Docente': 'BARRACO Maria Laura', 'Materia': 'Italiano e Latino', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['1B', '2F', '5B'], 'Giorno': 'Lunedì', 'Ora': '1ª ora (08:00)', 'DISP_Anno': 3, 'EXTRA_Anno': 1}
]

# Inizializzazione Registro Sostituzioni
if 'registro' not in st.session_state:
    st.session_state.registro = []

# Sidebar per inserimento assenza
st.sidebar.header("📋 Segnalazione Docente Assente")

docente_assente = st.sidebar.selectbox("Docente Assente", list(TEACHER_SCHEDULES.keys()), index=0)
giorno = st.sidebar.selectbox("Giorno della Settimana", ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì'], index=1)
ora = st.sidebar.selectbox("Ora di Lezione", ['1ª ora (08:00)', '2ª ora (08:55)', '3ª ora (10:00)', '4ª ora (10:55)', '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)'], index=3)

# Riconoscimento automatico della classe
teacher_info = TEACHER_SCHEDULES.get(docente_assente, {})
schedule = teacher_info.get('Orario', {}).get(giorno, {})
classe_rilevata = schedule.get(ora, None)

st.sidebar.markdown("---")
if classe_rilevata and classe_rilevata != 'DISP':
    st.sidebar.success(f"📍 **Classe rilevata automaticamente:** {classe_rilevata}")
    classe_effettiva = classe_rilevata
else:
    if classe_rilevata == 'DISP':
        st.sidebar.info(f"ℹ️ {docente_assente} era in ore a DISPOSIZIONE ({ora}).")
    else:
        st.sidebar.warning(f"⚠️ Nessuna classe a orario trovata per {docente_assente} il {giorno} alla {ora}.")
    classe_effettiva = st.sidebar.selectbox("Seleziona manualmente la classe da coprire:", list(CLASSES_INFO.keys()), index=31)

materia_docente = teacher_info.get('Materia', 'Disciplina Generale')
indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_effettiva, ('ITE', 'Istituto Tecnico Economico'))

st.markdown(f"## Ricerca Sostituto per **{docente_assente}** — {giorno}, {ora}")
st.info(f"📍 **Classe interessata:** `{classe_effettiva}` ({indirizzo_nome}) | 📚 **Materia da coprire:** `{materia_docente}`")

# Algoritmo di Ricerca Sostituti
cand_p1, cand_p2a, cand_p2b, cand_p3a, cand_p3b = [], [], [], [], []

for d in DISP_TEACHERS:
    if d['Giorno'] == giorno and d['Ora'] == ora:
        is_same_cdc = classe_effettiva in d['CdC']
        is_same_ind = d['Indirizzo'] == indirizzo_codice
        is_same_mat = d['Materia'] == materia_docente
        
        row = {
            'Docente': d['Docente'],
            'Materia': d['Materia'],
            'Indirizzo': d['Indirizzo'],
            'CdC': 'Sì' if is_same_cdc else 'No',
            'DISP_Anno': d['DISP_Anno'],
            'EXTRA_Anno': d['EXTRA_Anno']
        }
        
        if is_same_cdc:
            cand_p1.append(row)
        elif is_same_ind and is_same_mat:
            cand_p2a.append(row)
        elif is_same_ind:
            cand_p2b.append(row)
        elif is_same_mat:
            cand_p3a.append(row)
        else:
            cand_p3b.append(row)

sostituto_scelto = None
tipo_sostituzione = 'DISP (In Orario)'

# Output Graduatoria Priorità
if cand_p1:
    st.success("🟢 **PRIORITÀ 1: Docente a Disposizione nello Stesso Consiglio di Classe (CdC)**")
    df_p1 = pd.DataFrame(cand_p1)
    st.dataframe(df_p1, use_container_width=True)
    sostituto_scelto = cand_p1[0]['Docente']
    st.caption(f"💡 **Candidato consigliato:** {sostituto_scelto} (DISP In Orario - Stesso CdC `{classe_effettiva}`)")

elif cand_p2a:
    st.success("🟢 **PRIORITÀ 2a: Docente a Disposizione dello Stesso Indirizzo e Stessa Materia**")
    df_p2a = pd.DataFrame(cand_p2a)
    st.dataframe(df_p2a, use_container_width=True)
    sostituto_scelto = cand_p2a[0]['Docente']

elif cand_p2b:
    st.success("🟢 **PRIORITÀ 2b: Docente a Disposizione dello Stesso Indirizzo (Altra Materia)**")
    df_p2b = pd.DataFrame(cand_p2b)
    st.dataframe(df_p2b, use_container_width=True)
    sostituto_scelto = cand_p2b[0]['Docente']

elif cand_p3a or cand_p3b:
    st.warning("🟡 **PRIORITÀ 3: Docente a Disposizione di Altro Indirizzo**")
    df_p3 = pd.DataFrame(cand_p3a + cand_p3b)
    st.dataframe(df_p3, use_container_width=True)
    sostituto_scelto = (cand_p3a + cand_p3b)[0]['Docente']

else:
    st.error("🔴 **PRIORITÀ 4 (Fallback): Nessun docente in ora 'DISP' disponibile.**")
    st.markdown("### 📞 Elenco Docenti Contattabili Straordinari (Ora Buca / Extra Orario)")
    extra_docenti = [
        {'Docente': 'SERIOLI Romana Carolina', 'Materia': "Disegno e Storia dell'Arte", 'Stato': 'Ora Buca (Insegnamento 3ª e 5ª ora)', 'CdC': 'Sì (2b)', 'Tipo': 'Ora Buca'},
        {'Docente': 'CASALI Federico', 'Materia': 'Scienze Motorie', 'Stato': 'Entrata Anticipata (+1 ora)', 'CdC': 'Sì (2b)', 'Tipo': 'Entrata Anticipata'},
        {'Docente': 'DE TURSI', 'Materia': 'Scienze Naturali', 'Stato': 'Uscita Posticipata (+1 ora)', 'CdC': 'Sì (2b)', 'Tipo': 'Uscita Posticipata'}
    ]
    df_extra = pd.DataFrame(extra_docenti)
    st.dataframe(df_extra, use_container_width=True)
    sostituto_scelto = extra_docenti[0]['Docente']
    tipo_sostituzione = 'EXTRA (Fuori Orario)'

# Assegnazione
col1, col2 = st.columns([3, 1])
with col1:
    docente_final = st.selectbox("Seleziona / Conferma il docente sostituto:", [sostituto_scelto] if sostituto_scelto else ['Nessuno'])
with col2:
    st.write("")
    st.write("")
    if st.button("✅ Conferma Assegnazione e Registra", type="primary"):
        st.session_state.registro.append({
            'Data / Giorno': f"{giorno} ({ora})",
            'Docente Assente': docente_assente,
            'Classe': classe_effettiva,
            'Docente Sostituto': docente_final,
            'Tipologia': tipo_sostituzione
        })
        st.success(f"Sostituzione registrata per {docente_final} nella classe {classe_effettiva}!")

# Registro Annuale
st.markdown("---")
st.subheader("📊 Registro Annuale Sostituzioni e Conteggio Ore")

if st.session_state.registro:
    df_reg = pd.DataFrame(st.session_state.registro)
    st.dataframe(df_reg, use_container_width=True)
else:
    st.info("Nessuna sostituzione ancora confermata nel registro annuale.")
