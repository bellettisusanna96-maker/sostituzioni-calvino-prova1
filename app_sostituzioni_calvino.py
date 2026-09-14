import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Gestione Sostituzioni - I.I.S. Italo Calvino", page_icon="🏫", layout="wide")

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

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

def load_and_normalize_schedule(uploaded_file):
    is_csv = uploaded_file.name.endswith('.csv')
    file_bytes = uploaded_file.getvalue()
    
    if is_csv:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding='latin1')
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    doc_col = None
    for col in df.columns:
        if str(col).strip().upper() in ['DOCENTE', 'PROFESSORE', 'INSEGNANTE', 'NOME']:
            doc_col = col
            break

    if not doc_col:
        header_row_idx = None
        for idx in range(min(15, len(df))):
            row_vals = [str(x).strip().upper() for x in df.iloc[idx].values]
            if 'DOCENTE' in row_vals or 'PROFESSORE' in row_vals or 'MATERIA' in row_vals:
                header_row_idx = idx + 1
                break
        if header_row_idx is not None:
            if is_csv:
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), skiprows=header_row_idx)
                except Exception:
                    df = pd.read_csv(io.BytesIO(file_bytes), skiprows=header_row_idx, encoding='latin1')
            else:
                df = pd.read_excel(io.BytesIO(file_bytes), skiprows=header_row_idx)

    col_mapping = {}
    days_map = {'LUN': 'Lunedì', 'MAR': 'Martedì', 'MER': 'Mercoledì', 'GIO': 'Giovedì', 'VEN': 'Venerdì'}
    time_slots = ['1ª ora (08:00)', '2ª ora (08:55)', '3ª ora (10:00)', '4ª ora (10:55)', '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)']

    for col in df.columns:
        c_str = str(col).strip()
        c_upper = c_str.upper()
        if c_upper in ['DOCENTE', 'PROFESSORE', 'NOME']:
            col_mapping[col] = 'Docente'
        elif c_upper in ['MATERIA', 'DISCIPLINA']:
            col_mapping[col] = 'Materia'
        elif c_upper in ['INDIRIZZO']:
            col_mapping[col] = 'Indirizzo'
        elif c_upper in ['CDC', 'CONSIGLI DI CLASSE']:
            col_mapping[col] = 'CdC'
        else:
            for code, full in days_map.items():
                if code in c_upper or full.upper() in c_upper:
                    for slot in time_slots:
                        ora_short = slot.split(' ')[0]
                        if ora_short in c_str:
                            col_mapping[col] = f'{full}_{slot}'
                            break

    df = df.rename(columns=col_mapping)

    if 'Docente' in df.columns:
        df = df[df['Docente'].notna() & (df['Docente'].astype(str).str.strip() != '') & (~df['Docente'].astype(str).str.upper().str.contains('DOCENTE'))]

    # Auto-infer CdC e Indirizzo se mancanti o incompleti
    if 'Docente' in df.columns:
        cdc_list_built = []
        ind_list_built = []
        for _, row in df.iterrows():
            classes_found = set()
            for col in df.columns:
                if '_' in col and any(g in col for g in GIORNI):
                    val = str(row[col]).strip()
                    if val and val.upper() != 'DISP' and val != 'nan' and val in CLASSES_INFO:
                        classes_found.add(val)
            
            existing_cdc = str(row.get('CdC', '')).strip()
            if existing_cdc and existing_cdc != 'nan':
                cdc_str = existing_cdc
            else:
                cdc_str = ", ".join(sorted(list(classes_found)))
            cdc_list_built.append(cdc_str)
            
            existing_ind = str(row.get('Indirizzo', '')).strip()
            if existing_ind and existing_ind != 'nan':
                ind_str = existing_ind
            else:
                # Infer from classes
                inds = set(CLASSES_INFO[c][0] for c in classes_found if c in CLASSES_INFO)
                ind_str = list(inds)[0] if len(inds) > 0 else 'ITE'
            ind_list_built.append(ind_str)
            
        df['CdC'] = cdc_list_built
        df['Indirizzo'] = ind_list_built

    return df

if 'registro' not in st.session_state:
    st.session_state.registro = []

st.sidebar.header("📁 Caricamento Orario Scolastico")
uploaded_file = st.sidebar.file_uploader("Carica File Orario (Excel / CSV)", type=['xlsx', 'csv'])

st.sidebar.markdown("---")
st.sidebar.header("📋 Segnalazione Docente Assente")

default_teachers_data = [
    {
        'Docente': 'ACCIAVATTI Luciana', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '3B, 4B, 5B, 4H',
        'Lunedì_1ª ora (08:00)': '5B', 'Lunedì_2ª ora (08:55)': '4B', 'Lunedì_3ª ora (10:00)': '3B', 'Lunedì_4ª ora (10:55)': 'DISP', 'Lunedì_5ª ora (12:00)': '5B', 'Lunedì_6ª ora (12:55)': '4H', 'Lunedì_7ª ora (14:00)': '4H',
        'Martedì_1ª ora (08:00)': '5B', 'Martedì_2ª ora (08:55)': '4B', 'Martedì_3ª ora (10:00)': '4B', 'Martedì_4ª ora (10:55)': '3B', 'Martedì_5ª ora (12:00)': '5B',
        'Mercoledì_1ª ora (08:00)': '3B', 'Mercoledì_2ª ora (08:55)': '5B', 'Mercoledì_3ª ora (10:00)': '3B', 'Mercoledì_4ª ora (10:55)': '4B', 'Mercoledì_5ª ora (12:00)': '4B',
        'Giovedì_1ª ora (08:00)': '3B'
    },
    {
        'Docente': 'BELLETTI Susanna', 'Materia': 'Scienze Motorie', 'Indirizzo': 'ITE',
        'CdC': '1b, 2b, 3b, 4b, 5b, 3c, 4c, 5c, 3e',
        'Lunedì_5ª ora (12:00)': '2b', 'Lunedì_6ª ora (12:55)': '4b', 'Lunedì_7ª ora (14:00)': '3c',
        'Martedì_3ª ora (10:00)': '5c', 'Martedì_4ª ora (10:55)': '2b', 'Martedì_5ª ora (12:00)': '5b', 'Martedì_6ª ora (12:55)': '3b', 'Martedì_7ª ora (14:00)': '1b',
        'Mercoledì_1ª ora (08:00)': '3e', 'Mercoledì_2ª ora (08:55)': '3e', 'Mercoledì_3ª ora (10:00)': '5c', 'Mercoledì_4ª ora (10:55)': '4b',
        'Giovedì_3ª ora (10:00)': '3b', 'Giovedì_4ª ora (10:55)': '4c',
        'Venerdì_5ª ora (12:00)': '1b', 'Venerdì_6ª ora (12:55)': '5b'
    }
]

if uploaded_file is not None:
    try:
        df_schedule = load_and_normalize_schedule(uploaded_file)
        if 'Docente' not in df_schedule.columns or len(df_schedule) == 0:
            st.sidebar.error("⚠️ Impossibile rilevare la colonna 'Docente' nel file. Verificare la struttura.")
            df_schedule = pd.DataFrame(default_teachers_data)
        else:
            st.sidebar.success(f"✅ Caricato file: `{uploaded_file.name}` ({len(df_schedule)} docenti)")
    except Exception as e:
        st.sidebar.error(f"Errore nella lettura del file: {e}")
        df_schedule = pd.DataFrame(default_teachers_data)
else:
    df_schedule = pd.DataFrame(default_teachers_data)

docente_list = sorted(df_schedule['Docente'].astype(str).unique().tolist())
docente_assente = st.sidebar.selectbox("Docente Assente", docente_list, index=0)
giorno = st.sidebar.selectbox("Giorno della Settimana", GIORNI, index=1)
ora = st.sidebar.selectbox("Ora di Lezione", ORE, index=3)

rows_assente = df_schedule[df_schedule['Docente'] == docente_assente]
if len(rows_assente) > 0:
    row_doc = rows_assente.iloc[0]
else:
    row_doc = df_schedule.iloc[0]

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

materia_docente = str(row_doc.get('Materia', 'Generale'))
indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_effettiva, ('ITE', 'Istituto Tecnico Economico'))

st.markdown(f"## Ricerca Sostituto per **{docente_assente}** — {giorno}, {ora}")
st.info(f"📍 **Classe interessata:** `{classe_effettiva}` ({indirizzo_nome}) | 📚 **Materia da coprire:** `{materia_docente}`")

candidati_disp = []
candidati_extra = []

for idx, r in df_schedule.iterrows():
    d_nome = str(r['Docente']).strip()
    if d_nome == docente_assente:
        continue
    
    d_mat = str(r.get('Materia', '')).strip()
    d_ind = str(r.get('Indirizzo', '')).strip()
    d_cdc_list = [c.strip() for c in str(r.get('CdC', '')).split(',') if c.strip()]
    
    is_cdc = classe_effettiva in d_cdc_list
    is_ind = (d_ind == indirizzo_codice)
    is_mat = (d_mat == materia_docente)
    
    val_ora = str(r.get(slot_key, '')).strip()
    
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
        
    elif val_ora == '' or val_ora == 'nan':
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

st.markdown("---")
st.subheader("📊 Registro Annuale Sostituzioni")
if st.session_state.registro:
    df_reg = pd.DataFrame(st.session_state.registro)
    st.dataframe(df_reg, use_container_width=True)
else:
    st.info("Nessuna sostituzione registrata al momento.")
