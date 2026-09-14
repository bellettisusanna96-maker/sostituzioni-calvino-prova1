import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestione Sostituzioni - I.I.S. Italo Calvino", page_icon="🏫", layout="wide")

# Intestazione
st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

# -----------------------------------------------------------------------------
# 1. DATABASE CLASSI E INFORMAZIONI INDIRIZZO
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 2. CONSIGLI DI CLASSE (CdC) REALI ED ESATTI
# -----------------------------------------------------------------------------
CLASS_CDC = {
    '5b': ['BELLETTI Susanna', 'BONO Lamberto', 'SALVATI Salvatore', 'GRASSI Valentina', 'CATTANEI Giuseppe', 'ALBANESE Alessandra', 'GUARNIERI Oriana', 'VACANTE 3 (Informatica)'],
    '2b': ['BELLETTI Susanna', 'FEDELI Angelo', 'GRASSI Valentina', 'SALVATI Salvatore', 'DE TURSI', 'CATTANEI Giuseppe', 'ALBANESE Alessandra', 'SERIOLI Romana Carolina', 'CASALI Federico'],
    '5B': ['ACCIAVATTI Luciana', 'BARRACO Maria Laura', 'DE CASTRO Calogero', 'COMINI Fabio', 'VILLA Elena', 'MARIANI Paolo'],
    '4B': ['ACCIAVATTI Luciana', 'BARRACO Maria Laura', 'DE CASTRO Calogero', 'COMINI Fabio'],
    '3B': ['ACCIAVATTI Luciana', 'BARRACO Maria Laura', 'DE CASTRO Calogero'],
    '2a': ['BELLETTI Susanna', 'FEDELI Angelo', 'BONO Lamberto'],
    '5c': ['BELLETTI Susanna', 'FEDELI Angelo', 'BONO Lamberto']
}

# -----------------------------------------------------------------------------
# 3. DATABASE ORARIO COMPLETO DOCENTI
# -----------------------------------------------------------------------------
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
    'DE TURSI': {
        'Materia': 'Scienze Naturali',
        'Indirizzo': 'ITE',
        'CdC_Classi': ['2b', '3b', '4b'],
        'Orario': {
            'Martedì': {'3ª ora (10:00)': '2b', '4ª ora (10:55)': '3b', '5ª ora (12:00)': '4b'} # Ha lezione alla 5ª ora!
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
        'CdC_Classi': ['1a', '3a', '5a', '5b'],
        'Orario': {
            'Lunedì': {'2ª ora (08:55)': 'DISP', '6ª ora (12:55)': 'DISP'},
            'Martedì': {'5ª ora (12:00)': 'DISP'}
        }
    },
    'SALVATI Salvatore': {
        'Materia': 'Matematica',
        'Indirizzo': 'ITE',
        'CdC_Classi': ['2b', '5b'],
        'Orario': {
            'Martedì': {'3ª ora (10:00)': '5b', '4ª ora (10:55)': '5b', '6ª ora (12:55)': '2b'} # 5ª ora buca
        }
    },
    'COMINI Fabio': {
        'Materia': 'Filosofia e Storia',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['4D', '4A', '5A', '3D'],
        'Orario': {
            'Martedì': {'4ª ora (10:55)': 'DISP', '5ª ora (12:00)': 'DISP'}
        }
    },
    'BARRACO Maria Laura': {
        'Materia': 'Italiano e Latino',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['1B', '2F', '5B'],
        'Orario': {
            'Lunedì': {'1ª ora (08:00)': 'DISP'},
            'Martedì': {'5ª ora (12:00)': 'DISP'}
        }
    },
    'SERIOLI Romana Carolina': {
        'Materia': "Disegno e Storia dell'Arte",
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['2b', '3B', '4B'],
        'Orario': {
            'Martedì': {'3ª ora (10:00)': '2b', '6ª ora (12:55)': '3B'} # Ora buca 4ª e 5ª ora
        }
    },
    'CASALI Federico': {
        'Materia': 'Scienze Motorie',
        'Indirizzo': 'Liceo Scientifico',
        'CdC_Classi': ['2b', '1A', '2A'],
        'Orario': {
            'Martedì': {'6ª ora (12:55)': '2b', '7ª ora (14:00)': '2b'} # Entrata anticipata alla 5ª ora (+1 ora)
        }
    }
}

# -----------------------------------------------------------------------------
# 4. DOCENTI IN ORA DISP (DISPOSIZIONE)
# -----------------------------------------------------------------------------
DISP_TEACHERS = [
    {'Docente': 'BONO Lamberto', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['1a', '3a', '5a', '5b'], 'Giorno': 'Martedì', 'Ora': '5ª ora (12:00)', 'DISP_Anno': 4, 'EXTRA_Anno': 1},
    {'Docente': 'FEDELI Angelo', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['2b', '2c', '3d'], 'Giorno': 'Martedì', 'Ora': '5ª ora (12:00)', 'DISP_Anno': 1, 'EXTRA_Anno': 0},
    {'Docente': 'FEDELI Angelo', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['2b', '2c', '3d'], 'Giorno': 'Martedì', 'Ora': '4ª ora (10:55)', 'DISP_Anno': 1, 'EXTRA_Anno': 0},
    {'Docente': 'BONO Lamberto', 'Materia': 'Economia Aziendale', 'Indirizzo': 'ITE', 'CdC': ['1a', '3a', '5a', '5b'], 'Giorno': 'Lunedì', 'Ora': '2ª ora (08:55)', 'DISP_Anno': 4, 'EXTRA_Anno': 1},
    {'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['4D', '4A', '5A', '3D'], 'Giorno': 'Martedì', 'Ora': '4ª ora (10:55)', 'DISP_Anno': 5, 'EXTRA_Anno': 0},
    {'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['4D', '4A', '5A', '3D'], 'Giorno': 'Martedì', 'Ora': '5ª ora (12:00)', 'DISP_Anno': 5, 'EXTRA_Anno': 0},
    {'Docente': 'BARRACO Maria Laura', 'Materia': 'Italiano e Latino', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['1B', '2F', '5B'], 'Giorno': 'Lunedì', 'Ora': '1ª ora (08:00)', 'DISP_Anno': 3, 'EXTRA_Anno': 1},
    {'Docente': 'BARRACO Maria Laura', 'Materia': 'Italiano e Latino', 'Indirizzo': 'Liceo Scientifico', 'CdC': ['1B', '2F', '5B'], 'Giorno': 'Martedì', 'Ora': '5ª ora (12:00)', 'DISP_Anno': 3, 'EXTRA_Anno': 1}
]

# Inizializzazione Registro Sostituzioni
if 'registro' not in st.session_state:
    st.session_state.registro = []

# Sidebar per inserimento assenza
st.sidebar.header("📋 Segnalazione Docente Assente")

docente_assente = st.sidebar.selectbox("Docente Assente", list(TEACHER_SCHEDULES.keys()), index=0)
giorno = st.sidebar.selectbox("Giorno della Settimana", ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì'], index=1)
ora = st.sidebar.selectbox("Ora di Lezione", ['1ª ora (08:00)', '2ª ora (08:55)', '3ª ora (10:00)', '4ª ora (10:55)', '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)'], index=4)

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
    classe_effettiva = st.sidebar.selectbox("Seleziona manualmente la classe da coprire:", list(CLASSES_INFO.keys()), index=34)

materia_docente = teacher_info.get('Materia', 'Disciplina Generale')
indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_effettiva, ('ITE', 'Istituto Tecnico Economico'))

st.markdown(f"## Ricerca Sostituto per **{docente_assente}** — {giorno}, {ora}")
st.info(f"📍 **Classe interessata:** `{classe_effettiva}` ({indirizzo_nome}) | 📚 **Materia da coprire:** `{materia_docente}`")

# Recupera CdC effettivo della classe da coprire
cdc_classe_effettiva = CLASS_CDC.get(classe_effettiva, [docente_assente])

# Algoritmo di Ricerca Sostituti
cand_p1, cand_p2a, cand_p2b, cand_p3a, cand_p3b = [], [], [], [], []
tutti_candidati = []

for d in DISP_TEACHERS:
    if d['Giorno'] == giorno and d['Ora'] == ora and d['Docente'] != docente_assente:
        is_same_cdc = (classe_effettiva in d['CdC']) or (d['Docente'] in cdc_classe_effettiva)
        is_same_ind = d['Indirizzo'] == indirizzo_codice
        is_same_mat = d['Materia'] == materia_docente
        
        row = {
            'Docente': d['Docente'],
            'Materia': d['Materia'],
            'Indirizzo': d['Indirizzo'],
            'Stato': 'DISP (In Orario)',
            'CdC': f'Sì ({classe_effettiva})' if is_same_cdc else 'No',
            'Tipo_Ore': 'DISP',
            'DISP_Anno': d['DISP_Anno'],
            'EXTRA_Anno': d['EXTRA_Anno']
        }
        
        if is_same_cdc:
            row['Priorità'] = 'Priorità 1 (Stesso CdC)'
            cand_p1.append(row)
        elif is_same_ind and is_same_mat:
            row['Priorità'] = 'Priorità 2a (Stesso Indirizzo / Stessa Materia)'
            cand_p2a.append(row)
        elif is_same_ind:
            row['Priorità'] = 'Priorità 2b (Stesso Indirizzo / Altra Materia)'
            cand_p2b.append(row)
        elif is_same_mat:
            row['Priorità'] = 'Priorità 3a (Altro Indirizzo / Stessa Materia)'
            cand_p3a.append(row)
        else:
            row['Priorità'] = 'Priorità 3b (Altro Indirizzo / Altra Materia)'
            cand_p3b.append(row)
            
        tutti_candidati.append(row)

# Ricerca Docenti per Supplenza Straordinaria (Ora Buca / Extra Orario)
cand_extra = []
# Esempio dinamico in base al giorno/ora
if giorno == 'Martedì' and ora == '5ª ora (12:00)':
    # SALVATI ha ora buca ed è nel CdC di 5b!
    cand_extra.append({
        'Docente': 'SALVATI Salvatore', 'Materia': 'Matematica', 'Indirizzo': 'ITE', 
        'Stato': 'Ora Buca', 'CdC': f'Sì ({classe_effettiva})', 'Tipo_Ore': 'EXTRA',
        'Priorità': f'Priorità 4 (Ora Buca - CdC {classe_effettiva})', 'DISP_Anno': 2, 'EXTRA_Anno': 1
    })
    # SERIOLI ha ora buca ma non è nel CdC di 5b (è nel CdC di 2b)
    cand_extra.append({
        'Docente': 'SERIOLI Romana Carolina', 'Materia': "Disegno e Storia dell'Arte", 'Indirizzo': 'Liceo Scientifico', 
        'Stato': 'Ora Buca', 'CdC': 'No (CdC 2b)', 'Tipo_Ore': 'EXTRA',
        'Priorità': 'Priorità 4 (Ora Buca - Altro CdC)', 'DISP_Anno': 1, 'EXTRA_Anno': 3
    })
    # CASALI entrata anticipata (+1 ora)
    cand_extra.append({
        'Docente': 'CASALI Federico', 'Materia': 'Scienze Motorie', 'Indirizzo': 'Liceo Scientifico', 
        'Stato': 'Entrata Anticipata (+1 ora)', 'CdC': 'No (CdC 2b)', 'Tipo_Ore': 'EXTRA',
        'Priorità': 'Priorità 4 (Entrata Anticipata)', 'DISP_Anno': 0, 'EXTRA_Anno': 2
    })

# Output Graduatoria e Visualizzazione Tabelle
if cand_p1:
    st.success("🟢 **PRIORITÀ 1: Docenti a Disposizione nello Stesso Consiglio di Classe (CdC)**")
    st.dataframe(pd.DataFrame(cand_p1), use_container_width=True)

if cand_p2a:
    st.success("🟢 **PRIORITÀ 2a: Docenti a Disposizione dello Stesso Indirizzo e Stessa Materia**")
    st.dataframe(pd.DataFrame(cand_p2a), use_container_width=True)

if cand_p2b:
    st.success("🟢 **PRIORITÀ 2b: Docenti a Disposizione dello Stesso Indirizzo (Altra Materia)**")
    st.dataframe(pd.DataFrame(cand_p2b), use_container_width=True)

if cand_p3a or cand_p3b:
    st.warning("🟡 **PRIORITÀ 3: Docenti a Disposizione di Altro Indirizzo**")
    st.dataframe(pd.DataFrame(cand_p3a + cand_p3b), use_container_width=True)

if cand_extra:
    st.error("🔴 **PRIORITÀ 4 (Fallback / Straordinario): Docenti Contattabili in Ora Buca / Fuori Orario**")
    st.dataframe(pd.DataFrame(cand_extra), use_container_width=True)

# -----------------------------------------------------------------------------
# SELEZIONE INTERATTIVA DEL SOSTITUTO PREFERITO DALLA VICEPRESIDENZA
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🎯 Selezione e Assegnazione Manuale/Automatica del Sostituto")

lista_opzioni_sostituti = []
# Aggiunge tutti i candidati DISP
for c in tutti_candidati:
    label = f"[{c['Priorità']}] {c['Docente']} ({c['Materia']} - {c['Indirizzo']}) | Ore DISP Anno: {c['DISP_Anno']}"
    lista_opzioni_sostituti.append((label, c))

# Aggiunge i candidati EXTRA
for c in cand_extra:
    label = f"[{c['Priorità']}] {c['Docente']} ({c['Materia']} - {c['Stato']}) | Ore EXTRA Anno: {c['EXTRA_Anno']}"
    lista_opzioni_sostituti.append((label, c))

if lista_opzioni_sostituti:
    labels = [op[0] for op in lista_opzioni_sostituti]
    
    scelta_label = st.selectbox(
        "👉 **Seleziona il docente che preferisci assegnare tra TUTTI i candidati identificati:**",
        options=labels,
        index=0
    )
    
    # Recupera l'oggetto candidato selezionato
    candidato_selezionato = next(op[1] for op in lista_opzioni_sostituti if op[0] == scelta_label)
    
    st.markdown(f"**Docente Selezionato:** `{candidato_selezionato['Docente']}` | **Tipo Sostituzione:** `{candidato_selezionato['Tipo_Ore']}` | **Priorità:** `{candidato_selezionato['Priorità']}`")
    
    if st.button("✅ Conferma e Registra Sostituzione Nel Registro Annuale", type="primary"):
        st.session_state.registro.append({
            'Docente Sostituto': candidato_selezionato['Docente'],
            'Docente Assente': docente_assente,
            'Classe': classe_effettiva,
            'Giorno': giorno,
            'Ora': ora,
            'Tipologia': candidato_selezionato['Tipo_Ore'],
            'Priorità Applicata': candidato_selezionato['Priorità']
        })
        st.success(f"🎉 Sostituzione registrata con successo! Assegnata a **{candidato_selezionato['Docente']}**.")

else:
    st.error("Nessun docente candidato trovato per questa specifica ora/giorno.")

# -----------------------------------------------------------------------------
# REGISTRO ANNUALE SOSTITUZIONI
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Registro Annuale Sostituzioni e Conteggio Ore")

if st.session_state.registro:
    df_reg = pd.DataFrame(st.session_state.registro)
    st.dataframe(df_reg, use_container_width=True)
    
    # Grafico riepilogativo per docente
    st.bar_chart(df_reg.groupby(['Docente Sostituto', 'Tipologia']).size().unstack(fill_value=0))
else:
    st.info("Nessuna sostituzione ancora registrata nel registro annuale. Effettua la prima selezione sopra!")
