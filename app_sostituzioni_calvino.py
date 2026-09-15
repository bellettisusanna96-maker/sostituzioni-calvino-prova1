import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Gestione Sostituzioni - I.I.S. Italo Calvino",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze - Modulo Multi-Assenze con Cancellazione Singola (A.S. 2026/2027)")

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

# Inizializzazione Session State
if 'assenze_giorno' not in st.session_state:
    st.session_state.assenze_giorno = [] # lista di dict: {'Docente': str, 'Tipo': str, 'Ore': [str]}

if 'registro' not in st.session_state:
    st.session_state.registro = []

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
    time_slots = ORE

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
                inds = set(CLASSES_INFO[c][0] for c in classes_found if c in CLASSES_INFO)
                ind_str = list(inds)[0] if len(inds) > 0 else 'ITE'
            ind_list_built.append(ind_str)
            
        df['CdC'] = cdc_list_built
        df['Indirizzo'] = ind_list_built

    return df

st.sidebar.header("📁 1. Caricamento Orario")
uploaded_file = st.sidebar.file_uploader("Carica File Orario (Excel / CSV)", type=['xlsx', 'csv'])

default_teachers_data = [
    {
        'Docente': 'ACCIAVATTI Luciana', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '3B, 4B, 5B, 4H',
        'Lunedì_1ª ora (08:00)': '5B', 'Lunedì_2ª ora (08:55)': '4B', 'Lunedì_3ª ora (10:00)': '3B', 'Lunedì_4ª ora (10:55)': 'DISP', 'Lunedì_5ª ora (12:00)': '5B', 'Lunedì_6ª ora (12:55)': '4H', 'Lunedì_7ª ora (14:00)': '4H',
        'Martedì_1ª ora (08:00)': '5B', 'Martedì_2ª ora (08:55)': '4B', 'Martedì_3ª ora (10:00)': '4B', 'Martedì_4ª ora (10:55)': '3B', 'Martedì_5ª ora (12:00)': '5B'
    },
    {
        'Docente': 'AGORINI', 'Materia': 'Lab. Informatica (Compresenza)', 'Indirizzo': 'ITE',
        'CdC': '3c, 4c, 5c',
        'Lunedì_5ª ora (12:00)': '3c', 'Lunedì_6ª ora (12:55)': '3c', 'Lunedì_7ª ora (14:00)': '4c'
    },
    {
        'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico',
        'CdC': '4A, 5A, 3D, 4D',
        'Lunedì_1ª ora (08:00)': '4A', 'Lunedì_2ª ora (08:55)': '4A', 'Lunedì_3ª ora (10:00)': '4D', 'Lunedì_4ª ora (10:55)': '5A', 'Lunedì_5ª ora (12:00)': '5A', 'Lunedì_6ª ora (12:55)': '5A'
    }
]

if uploaded_file is not None:
    try:
        df_schedule = load_and_normalize_schedule(uploaded_file)
        st.sidebar.success(f"✅ Caricato: `{uploaded_file.name}` ({len(df_schedule)} docenti)")
    except Exception as e:
        st.sidebar.error(f"Errore caricamento: {e}")
        df_schedule = pd.DataFrame(default_teachers_data)
else:
    df_schedule = pd.DataFrame(default_teachers_data)

st.sidebar.markdown("---")
st.sidebar.header("📅 2. Selezione Giorno")
giorno_selezionato = st.sidebar.selectbox("Giorno di Gestione Supplenze", GIORNI, index=0)

# Reset assenze se si cambia giorno (con conferma)
if 'giorno_corrente' not in st.session_state:
    st.session_state.giorno_corrente = giorno_selezionato
elif st.session_state.giorno_corrente != giorno_selezionato:
    st.session_state.giorno_corrente = giorno_selezionato
    st.session_state.assenze_giorno = []

# TABS PRINCIPALI DELL'INTERFACCIA
tab_assenze, tab_sostituzioni, tab_registro = st.tabs([
    "📋 1. Inserimento Assenze del Giorno",
    "🎯 2. Quadro Ore Scoperte e Assegnazione Sostituti",
    "📊 3. Registro e Report Giornaliero"
])

# ==============================================================================
# TAB 1: INSERIMENTO ASSENZE MULTI-DOCENTE
# ==============================================================================
with tab_assenze:
    st.markdown(f"### 📋 Registrazione Assenze e Permessi per **{giorno_selezionato}**")
    st.write("Inserisci **tutti i docenti assenti della giornata** prima di assegnare le supplenze. L'algoritmo escluderà automaticamente questi docenti dalle disponibilità per evitare doppi incarichi.")
    
    col_add1, col_add2, col_add3 = st.columns([2, 2, 3])
    
    docenti_disponibili_list = sorted(df_schedule['Docente'].astype(str).unique().tolist())
    
    with col_add1:
        doc_ass_sel = st.selectbox("Seleziona Docente Assente", docenti_disponibili_list, key="sel_doc_ass")
    
    # Trova lezioni del docente per il giorno
    r_doc = df_schedule[df_schedule['Docente'] == doc_ass_sel]
    r_info = r_doc.iloc[0] if len(r_doc) > 0 else {}
    
    ore_lezione_doc = []
    ore_dict = {}
    for slot in ORE:
        val = str(r_info.get(f"{giorno_selezionato}_{slot}", '')).strip()
        if val and val.upper() != 'NAN' and val != '':
            ore_lezione_doc.append(slot)
            ore_dict[slot] = val
            
    with col_add2:
        tipo_assenza = st.radio("Tipologia Assenza", ["🔴 Tutto il Giorno", "🟡 Permesso Orario / Parziale"], key="rad_tipo_ass")
        
    with col_add3:
        if tipo_assenza == "🔴 Tutto il Giorno":
            ore_selezionate_ass = list(ore_lezione_doc)
            st.info(f"Verranno inserite tutte le {len(ore_selezionate_ass)} ore in orario del docente per {giorno_selezionato}.")
        else:
            if not ore_lezione_doc:
                st.warning("Nessuna lezione trovata a orario per questo docente.")
                ore_selezionate_ass = []
            else:
                ore_selezionate_ass = st.multiselect(
                    "Seleziona le ore di Permesso / Assenza:",
                    options=ore_lezione_doc,
                    default=ore_lezione_doc,
                    format_func=lambda s: f"{s} (Classe {ore_dict[s]})" if ore_dict[s] != 'DISP' else f"{s} (DISP)"
                )

    if st.button("➕ Aggiungi Docente all'Elenco Assenti del Giorno", type="primary"):
        gia_presente = False
        for item in st.session_state.assenze_giorno:
            if item['Docente'] == doc_ass_sel:
                gia_presente = True
                break
                
        if gia_presente:
            st.error(f"⚠️ {doc_ass_sel} è già stato inserito nell'elenco degli assenti per {giorno_selezionato}.")
        elif not ore_selezionate_ass and tipo_assenza != "🔴 Tutto il Giorno":
            st.error("Seleziona almeno un'ora di permesso/assenza.")
        else:
            st.session_state.assenze_giorno.append({
                'Docente': doc_ass_sel,
                'Materia': str(r_info.get('Materia', '')),
                'Tipo': tipo_assenza,
                'Ore': ore_selezionate_ass
            })
            st.success(f"Aggiunto **{doc_ass_sel}** all'elenco assenti!")
            st.rerun()

    st.markdown("---")
    st.subheader(f"📑 Elenco Docenti Assenti Confermati per {giorno_selezionato}")
    
    if st.session_state.assenze_giorno:
        table_data = []
        for idx, item in enumerate(st.session_state.assenze_giorno):
            ore_str = ", ".join([o.split(" ")[0] for o in item['Ore']]) if item['Ore'] else "Nessuna lezione"
            table_data.append({
                '#' : idx + 1,
                'Docente Assente': item['Docente'],
                'Materia': item['Materia'],
                'Tipologia': item['Tipo'],
                'Ore Coinvolte dall\'Assenza': ore_str
            })
            
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        st.markdown("##### 🗑️ Gestione e Rimozione Singoli Docenti Assenti")
        
        # Rimozione individuale tramite pulsanti dedicati per riga
        for idx, item in enumerate(list(st.session_state.assenze_giorno)):
            c1, c2, c3, c4 = st.columns([3, 2, 3, 2])
            with c1:
                st.write(f"👤 **{item['Docente']}** ({item['Materia']})")
            with c2:
                st.write(f"{item['Tipo']}")
            with c3:
                ore_txt = ", ".join([o.split(" ")[0] for o in item['Ore']]) if item['Ore'] else "Nessuna"
                st.write(f"Ore: {ore_txt}")
            with c4:
                if st.button(f"❌ Rimuovi", key=f"btn_remove_{idx}_{item['Docente']}"):
                    doc_removed = item['Docente']
                    # Rimuovi dall'elenco assenti
                    st.session_state.assenze_giorno = [x for x in st.session_state.assenze_giorno if x['Docente'] != doc_removed]
                    # Rimuovi anche eventuali sostituzioni collegate a questo docente
                    st.session_state.registro = [r for r in st.session_state.registro if not (r.get('Giorno') == giorno_selezionato and r.get('Docente Assente') == doc_removed)]
                    st.success(f"Rimesso in servizio **{doc_removed}** (rimosso dall'elenco assenti)!")
                    st.rerun()

        st.markdown("---")
        c_del1, c_del2 = st.columns([3, 1])
        with c_del2:
            if st.button("🗑️ Svuota Tutto l'Elenco Assenti"):
                st.session_state.assenze_giorno = []
                st.rerun()
    else:
        st.info("Nessun docente assente registrato per oggi. Seleziona i docenti in alto e clicca su 'Aggiungi'.")

# ==============================================================================
# TAB 2: QUADRO ORE SCOPERTE E ASSEGNAZIONE SOSTITUTI
# ==============================================================================
with tab_sostituzioni:
    st.markdown(f"### 🎯 Quadro Ore Scoperte e Ricerca Sostituti ({giorno_selezionato})")
    
    # Calcolo di TUTTI i docenti assenti per ciascuna ora specifica (con fallback sicuro)
    docenti_assenti_per_ora = {slot: set() for slot in ORE}
    for item in st.session_state.assenze_giorno:
        d_nome = item['Docente']
        for slot in item['Ore']:
            if slot in docenti_assenti_per_ora:
                docenti_assenti_per_ora[slot].add(d_nome)
            else:
                docenti_assenti_per_ora[slot] = {d_nome}
            
    # Calcolo di TUTTI i docenti già assegnati come sostituti per ciascuna ora
    docenti_sostituti_occupati_per_ora = {slot: set() for slot in ORE}
    for reg in st.session_state.registro:
        if reg.get('Giorno') == giorno_selezionato:
            s_ora = reg.get('Ora')
            if s_ora in docenti_sostituti_occupati_per_ora:
                docenti_sostituti_occupati_per_ora[s_ora].add(reg.get('Docente Sostituto'))
            else:
                docenti_sostituti_occupati_per_ora[s_ora] = {reg.get('Docente Sostituto')}

    # Generazione Elenco Completo Classi Scoperte
    classi_scoperte_lista = []
    
    for item in st.session_state.assenze_giorno:
        d_nome = item['Docente']
        r_doc = df_schedule[df_schedule['Docente'] == d_nome]
        r_info = r_doc.iloc[0] if len(r_doc) > 0 else {}
        d_mat = str(r_info.get('Materia', 'Generale'))
        
        for slot in item['Ore']:
            slot_key = f"{giorno_selezionato}_{slot}"
            cls_val = str(r_info.get(slot_key, '')).strip()
            
            sostituto_assegnato = None
            for reg in st.session_state.registro:
                if reg.get('Giorno') == giorno_selezionato and reg.get('Ora') == slot and reg.get('Docente Assente') == d_nome:
                    sostituto_assegnato = reg.get('Docente Sostituto')
                    break
                    
            if cls_val and cls_val.upper() != 'NAN' and cls_val != '':
                classi_scoperte_lista.append({
                    'Docente Assente': d_nome,
                    'Materia': d_mat,
                    'Ora': slot,
                    'Classe / Slot': cls_val,
                    'Sostituto Assegnato': sostituto_assegnato if sostituto_assegnato else "🔴 IN SOSPESO"
                })

    if not st.session_state.assenze_giorno:
        st.warning("⚠️ Nessun docente assente inserito nel TAB 1. Torna al primo passaggio per registrare le assenze.")
    elif not classi_scoperte_lista:
        st.info("Tutte le assenze inserite riguardano ore libere o non ci sono lezioni da coprire.")
    else:
        st.markdown("#### 📌 Tabellone Riassuntivo delle Ore da Coprire")
        df_scoperte = pd.DataFrame(classi_scoperte_lista)
        st.dataframe(df_scoperte, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔍 Assegnazione Sostituto per un'Ora Scoperta")
        
        opzioni_scoperte = []
        for idx, row_s in enumerate(classi_scoperte_lista):
            stato_icon = "🟢" if row_s['Sostituto Assegnato'] != "🔴 IN SOSPESO" else "🔴"
            opzioni_scoperte.append(f"{stato_icon} {row_s['Ora']} | Assente: {row_s['Docente Assente']} | Classe: {row_s['Classe / Slot']} | Sostituto: {row_s['Sostituto Assegnato']}")
            
        idx_scoperta_sel = st.selectbox("Seleziona la lezione da coprire:", range(len(opzioni_scoperte)), format_func=lambda i: opzioni_scoperte[i])
        
        target_slot = classi_scoperte_lista[idx_scoperta_sel]
        docente_assente_target = target_slot['Docente Assente']
        ora_target = target_slot['Ora']
        classe_target = target_slot['Classe / Slot']
        materia_target = target_slot['Materia']
        
        st.info(f"📍 **Dettagli Lezione:** `{giorno_selezionato}`, `{ora_target}` | **Docente Assente:** `{docente_assente_target}` | **Classe:** `{classe_target}` | **Materia:** `{materia_target}`")
        
        esclusi_assenti = docenti_assenti_per_ora.get(ora_target, set())
        esclusi_sostituti = docenti_sostituti_occupati_per_ora.get(ora_target, set())
        tot_esclusi = esclusi_assenti.union(esclusi_sostituti)
        
        st.caption(f"🛡️ **Sicurezza Anti-Sovrapposizione ({ora_target}):** {len(tot_esclusi)} docenti esclusi (di cui {len(esclusi_assenti)} assenti e {len(esclusi_sostituti)} già in supplenza).")
        
        slot_key_target = f"{giorno_selezionato}_{ora_target}"
        indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_target if classe_target != 'DISP' else '1a', ('ITE', 'Istituto Tecnico Economico'))
        
        candidati_disp = []
        candidati_extra = []
        
        for idx, r in df_schedule.iterrows():
            d_nome = str(r['Docente']).strip()
            
            if d_nome in tot_esclusi:
                continue
                
            d_mat = str(r.get('Materia', '')).strip()
            d_ind = str(r.get('Indirizzo', '')).strip()
            d_cdc_list = [c.strip() for c in str(r.get('CdC', '')).split(',') if c.strip()]
            
            is_cdc = (classe_target in d_cdc_list) if classe_target != 'DISP' else False
            is_ind = (d_ind == indirizzo_codice)
            is_mat = (d_mat == materia_target)
            
            val_ora = str(r.get(slot_key_target, '')).strip()
            
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
                    'CdC': f"Sì ({classe_target})" if is_cdc else "No",
                    'Priorità': prio,
                    'Tipo': 'DISP'
                })
                
            elif val_ora == '' or val_ora == 'nan':
                ora_idx = ORE.index(ora_target) if ora_target in ORE else 0
                h_before = str(r.get(f"{giorno_selezionato}_{ORE[ora_idx-1]}", '')).strip() if ora_idx > 0 else ''
                h_after = str(r.get(f"{giorno_selezionato}_{ORE[ora_idx+1]}", '')).strip() if ora_idx < len(ORE)-1 else ''
                
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
                        'CdC': f"Sì ({classe_target})" if is_cdc else "No",
                        'Priorità': 'Priorità 4 (Ora Buca / Extra)',
                        'Tipo': 'EXTRA'
                    })

        all_cands = candidati_disp + candidati_extra
        
        if all_cands:
            st.dataframe(pd.DataFrame(all_cands), use_container_width=True)
            
            labels_cands = [f"{c['Docente']} | {c['Priorità']} | {c['Stato']}" for c in all_cands]
            scelta_cand_idx = st.selectbox("Scegli il docente da assegnare a questa classe:", range(len(labels_cands)), format_func=lambda i: labels_cands[i])
            
            cand_scelto = all_cands[scelta_cand_idx]
            
            if st.button("✅ Conferma Assegnazione Sostituto", type="primary"):
                st.session_state.registro = [
                    reg for reg in st.session_state.registro 
                    if not (reg.get('Giorno') == giorno_selezionato and reg.get('Ora') == ora_target and reg.get('Docente Assente') == docente_assente_target)
                ]
                
                st.session_state.registro.append({
                    'Giorno': giorno_selezionato,
                    'Ora': ora_target,
                    'Docente Assente': docente_assente_target,
                    'Classe': classe_target,
                    'Materia': materia_target,
                    'Docente Sostituto': cand_scelto['Docente'],
                    'Tipologia Sostituzione': cand_scelto['Tipo'],
                    'Priorità Applicata': cand_scelto['Priorità']
                })
                st.success(f"Assegnato con successo **{cand_scelto['Docente']}** per la classe **{classe_target}** ({ora_target})!")
                st.rerun()
        else:
            st.error("🔴 Nessun docente disponibile o in ora buca trovato per questo slot tra quelli in servizio.")

# ==============================================================================
# TAB 3: REGISTRO E REPORT GIORNALIERO
# ==============================================================================
with tab_registro:
    st.markdown(f"### 📊 Registro delle Sostituzioni Assegnate per **{giorno_selezionato}**")
    
    reg_giorno = [r for r in st.session_state.registro if r.get('Giorno') == giorno_selezionato]
    
    if reg_giorno:
        df_reg_giorno = pd.DataFrame(reg_giorno)
        st.dataframe(df_reg_giorno, use_container_width=True)
        
        csv_data = df_reg_giorno.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Report Sostituzioni di Oggi (CSV)",
            data=csv_data,
            file_name=f"sostituzioni_{giorno_selezionato}_Calvino.csv",
            mime="text/csv"
        )
    else:
        st.info("Nessuna sostituzione ancora confermata per la giornata di oggi.")
        
    st.markdown("---")
    st.subheader("📜 Storico Completo Sessione (Tutti i Giorni)")
    if st.session_state.registro:
        st.dataframe(pd.DataFrame(st.session_state.registro), use_container_width=True)
        if st.button("🗑️ Cancella Tutto il Registro"):
            st.session_state.registro = []
            st.rerun()
    else:
        st.info("Il registro generale è vuoto.")
