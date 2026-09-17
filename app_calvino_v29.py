import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Gestione Sostituzioni - I.I.S. Italo Calvino",
    page_icon="🏫",
    layout="wide"
)

### Tentativo di importazione di GSheetsConnection da streamlit_gsheets
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze - Modulo Gestione Settimanale e Storico Assenze (A.S. 2026/2027 - v29)")

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
ORE = [
    '1ª ora (08:00)', '2ª ora (08:55)', '3ª ora (10:00)', '4ª ora (10:55)',
    '5ª ora (12:00)', '6ª ora (12:55)', '7ª ora (14:00)'
]

def sort_registro_by_day_and_teacher(records):
    def sort_key(r):
        g_val = r.get('Giorno', '')
        g_idx = GIORNI.index(g_val) if g_val in GIORNI else 99
        d_ass = str(r.get('Docente Assente', '')).strip().upper()
        o_val = str(r.get('Ora', ''))
        o_idx = 99
        for i, slot in enumerate(ORE):
            if slot == o_val or slot.split(' ')[0] in o_val or o_val.split(' ')[0] in slot:
                o_idx = i
                break
        return (g_idx, d_ass, o_idx, str(r.get('Classe', '')))
    return sorted(records, key=sort_key)

def is_docente_assente_in_ora(doc_nome, giorno, ora_slot):
    """Verifica tassativa se un docente risulta assente in un determinato giorno e ora."""
    if 'assenze_per_giorno' not in st.session_state:
        return False
    for item in st.session_state.assenze_per_giorno.get(giorno, []):
        if item['Docente'] == doc_nome:
            if item.get('Tipo') == "🔴 Tutto il Giorno":
                return True
            if ora_slot in item.get('Ore', []):
                return True
    return False



### Inizializzazione Connessione Google Fogli
conn = None
gsheets_connected = False

if HAS_GSHEETS:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        gsheets_connected = True
    except Exception:
        gsheets_connected = False
else:
    try:
        conn = st.connection("gsheets")
        gsheets_connected = True
    except Exception:
        gsheets_connected = False

def load_data_from_gsheets():
    """Carica i dati salvati su Google Fogli nelle schede 'Assenze' e 'Registro'."""
    if not gsheets_connected or conn is None:
        return False, "Connessione non configurata"
    try:
        # Caricamento Scheda Assenze
        df_ass = None
        try:
            df_ass = conn.read(worksheet="Assenze", ttl=0)
        except Exception as e_ass:
            # Se la scheda è vuota o genera eccezione di lettura vuota, proseguiamo
            pass

        if df_ass is not None and not df_ass.empty:
            ass_per_giorno = {g: [] for g in GIORNI}
            for _, row in df_ass.iterrows():
                g = str(row.get('Giorno', '')).strip()
                doc = str(row.get('Docente', '')).strip()
                mat = str(row.get('Materia', '')).strip()
                ind = str(row.get('Indirizzo', '')).strip()
                tipo = str(row.get('Tipo', '')).strip()
                ore_raw = str(row.get('Ore', '')).strip()
                if g in ass_per_giorno and doc and doc != 'nan':
                    ore_list = [o.strip() for o in ore_raw.split(',') if o.strip() and o.strip() != 'nan'] if ore_raw else []
                    ass_per_giorno[g].append({
                        'Docente': doc,
                        'Materia': mat,
                        'Indirizzo': ind,
                        'Tipo': tipo,
                        'Ore': ore_list
                    })
            st.session_state.assenze_per_giorno = ass_per_giorno

        # Caricamento Scheda Registro
        df_reg = None
        try:
            df_reg = conn.read(worksheet="Registro", ttl=0)
        except Exception as e_reg:
            pass

        if df_reg is not None and not df_reg.empty:
            reg_list = []
            for _, row in df_reg.iterrows():
                g = str(row.get('Giorno', '')).strip()
                ora = str(row.get('Ora', '')).strip()
                d_ass = str(row.get('Docente Assente', '')).strip()
                cls = str(row.get('Classe', '')).strip()
                mat = str(row.get('Materia', '')).strip()
                d_sost = str(row.get('Docente Sostituto', '')).strip()
                tipo = str(row.get('Tipologia Sostituzione', '')).strip()
                prio = str(row.get('Priorità Applicata', '')).strip()
                if g and d_ass and d_sost and d_ass != 'nan' and d_sost != 'nan':
                    reg_list.append({
                        'Giorno': g,
                        'Ora': ora,
                        'Docente Assente': d_ass,
                        'Classe': cls,
                        'Materia': mat,
                        'Docente Sostituto': d_sost,
                        'Tipologia Sostituzione': tipo,
                        'Priorità Applicata': prio
                    })
            st.session_state.registro = reg_list
        return True, "OK"
    except Exception as e:
        return False, str(e)

def save_data_to_gsheets():
    """Salva lo stato corrente delle assenze e del registro direttamente su Google Fogli."""
    if not gsheets_connected or conn is None:
        return False
    try:
        # Prepara DataFrame Assenze
        rows_ass = []
        for g, items in st.session_state.assenze_per_giorno.items():
            for item in items:
                rows_ass.append({
                    'Giorno': g,
                    'Docente': item.get('Docente', ''),
                    'Materia': item.get('Materia', ''),
                    'Indirizzo': item.get('Indirizzo', ''),
                    'Tipo': item.get('Tipo', ''),
                    'Ore': ", ".join(item.get('Ore', []))
                })
        df_ass = pd.DataFrame(rows_ass, columns=['Giorno', 'Docente', 'Materia', 'Indirizzo', 'Tipo', 'Ore'])
        try:
            conn.update(worksheet="Assenze", data=df_ass)
        except Exception:
            try:
                conn.create(worksheet="Assenze", data=df_ass)
            except Exception as e_c1:
                st.session_state.gsheets_last_error = f"Errore scheda Assenze: {e_c1}"
                return False

        # Prepara DataFrame Registro
        df_reg = pd.DataFrame(st.session_state.registro)
        if df_reg.empty:
            df_reg = pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Priorità Applicata'])
        try:
            conn.update(worksheet="Registro", data=df_reg)
        except Exception:
            try:
                conn.create(worksheet="Registro", data=df_reg)
            except Exception as e_c2:
                st.session_state.gsheets_last_error = f"Errore scheda Registro: {e_c2}"
                return False

        st.session_state.gsheets_last_error = None
        return True
    except Exception as e:
        st.session_state.gsheets_last_error = str(e)
        return False

##### Inizializzazione Session State
if 'assenze_per_giorno' not in st.session_state:
    st.session_state.assenze_per_giorno = {g: [] for g in GIORNI}
if 'registro' not in st.session_state:
    st.session_state.registro = []
if 'gsheets_loaded' not in st.session_state:
    st.session_state.gsheets_loaded = False
    if gsheets_connected:
        success_init, err_init = load_data_from_gsheets()
        if success_init:
            st.session_state.gsheets_loaded = True

def import_registro_from_csv(uploaded_csv_file, replace_existing=True):
    """
    Legge un file CSV esportato in precedenza dal Registro Sostituzioni 
    e ripristina i dati nella sessione corrente.
    """
    try:
        bytes_data = uploaded_csv_file.getvalue()
        try:
            df_imp = pd.read_csv(io.BytesIO(bytes_data))
        except Exception:
            df_imp = pd.read_csv(io.BytesIO(bytes_data), encoding='latin1')

        # Verifichiamo la presenza delle colonne minime richieste
        cols_required = ['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto']
        missing_cols = [c for c in cols_required if c not in df_imp.columns]
        
        if missing_cols:
            st.error(f"❌ Impossibile importare: Il file CSV non contiene le colonne richieste ({', '.join(missing_cols)}).")
            return False

        if replace_existing:
            st.session_state.registro = []
            
        import_count = 0
        docenti_assenti_trovati = {}

        for _, row in df_imp.iterrows():
            g = str(row.get('Giorno', '')).strip()
            ora = str(row.get('Ora', '')).strip()
            d_ass = str(row.get('Docente Assente', '')).strip()
            cls = str(row.get('Classe', '')).strip()
            mat = str(row.get('Materia', '')).strip()
            d_sost = str(row.get('Docente Sostituto', '')).strip()
            tipo = str(row.get('Tipologia Sostituzione', 'EXTRA')).strip()
            prio = str(row.get('Priorità Applicata', 'Ripristinato da CSV')).strip()

            if g and d_ass and d_sost and d_ass.lower() != 'nan' and d_sost.lower() != 'nan':
                duplicate = False
                for r in st.session_state.registro:
                    if r.get('Giorno') == g and r.get('Ora') == ora and r.get('Docente Assente') == d_ass and r.get('Classe') == cls:
                        duplicate = True
                        break
                
                if not duplicate:
                    st.session_state.registro.append({
                        'Giorno': g,
                        'Ora': ora,
                        'Docente Assente': d_ass,
                        'Classe': cls,
                        'Materia': mat,
                        'Docente Sostituto': d_sost,
                        'Tipologia Sostituzione': tipo,
                        'Priorità Applicata': prio
                    })
                    import_count += 1

                if g in GIORNI:
                    if g not in docenti_assenti_trovati:
                        docenti_assenti_trovati[g] = set()
                    docenti_assenti_trovati[g].add(d_ass)

        # Ripristiniamo i docenti assenti nell'elenco assenze se non presenti
        for g, doc_set in docenti_assenti_trovati.items():
            if g not in st.session_state.assenze_per_giorno:
                st.session_state.assenze_per_giorno[g] = []
            
            existing_docs = {item['Docente'] for item in st.session_state.assenze_per_giorno[g]}
            for d_name in doc_set:
                if d_name not in existing_docs:
                    st.session_state.assenze_per_giorno[g].append({
                        'Docente': d_name,
                        'Materia': 'Da Storico CSV',
                        'Indirizzo': 'ITE',
                        'Tipo': '🔴 Tutto il Giorno',
                        'Ore': ORE
                    })

        if gsheets_connected:
            save_data_to_gsheets()

        st.success(f"✅ Importazione completata! Ripristinate **{import_count}** sostituzioni.")
        return True
    except Exception as e:
        st.error(f"❌ Errore durante l'importazione del CSV: {e}")
        return False

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
                    if val and val.upper() not in ['DISP', 'D', 'DISPOSIZIONE'] and val != 'nan' and val in CLASSES_INFO:
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
        'Docente': 'ACCIAVATTI Luciana', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico', 'CdC': '3B, 4B, 5B, 4H',
        'Lunedì_1ª ora (08:00)': '5B', 'Lunedì_2ª ora (08:55)': '4B', 'Lunedì_3ª ora (10:00)': '3B',
        'Lunedì_4ª ora (10:55)': 'DISP', 'Lunedì_5ª ora (12:00)': '5B', 'Lunedì_6ª ora (12:55)': '4H', 'Lunedì_7ª ora (14:00)': '4H',
        'Martedì_1ª ora (08:00)': '5B', 'Martedì_2ª ora (08:55)': '4B', 'Martedì_3ª ora (10:00)': '4B',
        'Martedì_4ª ora (10:55)': '3B', 'Martedì_5ª ora (12:00)': '5B'
    },
    {
        'Docente': 'AGORINI', 'Materia': 'Lab. Informatica (Compresenza)', 'Indirizzo': 'ITE', 'CdC': '3c, 4c, 5c',
        'Lunedì_5ª ora (12:00)': '3c', 'Lunedì_6ª ora (12:55)': '3c', 'Lunedì_7ª ora (14:00)': '4c'
    },
    {
        'Docente': 'COMINI Fabio', 'Materia': 'Filosofia e Storia', 'Indirizzo': 'Liceo Scientifico', 'CdC': '4A, 5A, 3D, 4D',
        'Lunedì_1ª ora (08:00)': '4A', 'Lunedì_2ª ora (08:55)': '4A', 'Lunedì_3ª ora (10:00)': '4D',
        'Lunedì_4ª ora (10:55)': '5A', 'Lunedì_5ª ora (12:00)': '5A', 'Lunedì_6ª ora (12:55)': '5A'
    }
]

if uploaded_file is not None:
    try:
        df_schedule = load_and_normalize_schedule(uploaded_file)
        st.sidebar.success(f"✅ Caricato: {uploaded_file.name} ({len(df_schedule)} docenti)")
    except Exception as e:
        st.sidebar.error(f"Errore caricamento: {e}")
        df_schedule = pd.DataFrame(default_teachers_data)
else:
    df_schedule = pd.DataFrame(default_teachers_data)

st.sidebar.markdown("---")
st.sidebar.header("📅 2. Selezione Giorno")
giorno_selezionato = st.sidebar.selectbox("Giorno di Gestione Supplenze", GIORNI, index=0)

# Calcolo stato coperture del giorno per la Sidebar
tot_scop_g = 0
in_sosp_g = 0
confl_g = 0

if 'assenze_per_giorno' in st.session_state and giorno_selezionato in st.session_state.assenze_per_giorno:
    for item_ass in st.session_state.assenze_per_giorno[giorno_selezionato]:
        d_n = item_ass['Docente']
        r_d = df_schedule[df_schedule['Docente'] == d_n]
        r_i = r_d.iloc[0] if len(r_d) > 0 else {}
        ore_eff = item_ass['Ore'] if item_ass.get('Tipo') != "🔴 Tutto il Giorno" else ORE
        
        for slot_o in ore_eff:
            s_k = f"{giorno_selezionato}_{slot_o}"
            c_v = str(r_i.get(s_k, '')).strip()
            if c_v and c_v.upper() not in ['NAN', '', 'DISP', 'D', 'DISPOSIZIONE']:
                tot_scop_g += 1
                sost_ass = None
                for reg in st.session_state.get('registro', []):
                    if reg.get('Giorno') == giorno_selezionato and reg.get('Ora') == slot_o and reg.get('Docente Assente') == d_n:
                        sost_ass = reg.get('Docente Sostituto')
                        break
                if not sost_ass:
                    in_sosp_g += 1
                elif is_docente_assente_in_ora(sost_ass, giorno_selezionato, slot_o):
                    confl_g += 1

if tot_scop_g > 0:
    if in_sosp_g == 0 and confl_g == 0:
        st.sidebar.success(f"🎉 **{giorno_selezionato}**: TUTTE COPERTE! ({tot_scop_g}/{tot_scop_g})")
    else:
        cop_g = tot_scop_g - in_sosp_g - confl_g
        st.sidebar.warning(f"⏳ **{giorno_selezionato}**: {cop_g}/{tot_scop_g} coperte ({in_sosp_g} in sospeso)")

### SIDEBAR: RIPRISTINO / IMPORTAZIONE DA BACKUP CSV
st.sidebar.markdown("---")
st.sidebar.header("📥 Importa Storico da CSV")
uploaded_backup_csv = st.sidebar.file_uploader("Carica File CSV di Backup", type=['csv'], key="sidebar_csv_uploader")
if uploaded_backup_csv is not None:
    mode_imp = st.sidebar.radio("Modalità Importazione:", ["Sostituisci Registro", "Aggiungi al Registro"], key="radio_imp_mode")
    replace_flag = (mode_imp == "Sostituisci Registro")
    if st.sidebar.button("🔄 Ripristina Dati da CSV", type="primary"):
        if import_registro_from_csv(uploaded_backup_csv, replace_existing=replace_flag):
            st.rerun()

### SIDEBAR: STATO CONNESIONE GOOGLE FOGLI
st.sidebar.markdown("---")
st.sidebar.header("📊 Salva su Google Fogli")

if gsheets_connected:
    st.sidebar.success("🟩  **Google Fogli Collegato** ")
    if getattr(st.session_state, 'gsheets_last_error', None):
        st.sidebar.error(f"⚠️ **Errore Salvataggio Cloud:** {st.session_state.gsheets_last_error}")
    if st.sidebar.button("🔄 Sincronizza / Ricarica da Cloud"):
        success, err_msg = load_data_from_gsheets()
        if success:
            st.sidebar.success("Dati ricaricati con successo!")
            st.rerun()
        else:
            st.sidebar.error(f"Errore durante la lettura da Google Fogli: {err_msg}")
else:
    st.sidebar.info("🟧  **Google Fogli Non Configurato** ")
    st.sidebar.caption("I dati vengono salvati temporaneamente in memoria sessione. Collega Google Fogli per il salvataggio cloud permanente.")

with st.sidebar.expander("ℹ️ Guida Collegamento Google Fogli"):
    st.markdown("""
    **Come attivare Google Fogli:**
    1. Crea un foglio su Google Fogli chiamato **Sostituzioni_Calvino** con due schede: Assenze e Registro.
    2. Condividi il foglio con l'email del tuo Service Account Google (con permessi di modifica).
    3. Su Streamlit Cloud, vai su **Settings -> Secrets** e inserisci le credenziali [connections.gsheets].
    4. Assicurati che st-gsheets-connection sia presente nel file requirements.txt.
    """)

if st.sidebar.button("🗑️ Reset Dati Nuova Settimana"):
    st.session_state.assenze_per_giorno = {g: [] for g in GIORNI}
    st.session_state.registro = []
    if gsheets_connected:
        save_data_to_gsheets()
    st.rerun()

##### Gestione dinamica assenze per giorno
st.session_state.giorno_corrente = giorno_selezionato
if giorno_selezionato not in st.session_state.assenze_per_giorno:
    st.session_state.assenze_per_giorno[giorno_selezionato] = []

assenze_giorno = st.session_state.assenze_per_giorno[giorno_selezionato]

### RILEVAMENTO GLOBALE CONFLITTI SUPPLENTI ASSENTI
conflitti_attivi = []
for reg in st.session_state.registro:
    g_reg = reg.get('Giorno')
    o_reg = reg.get('Ora')
    sost_nome = reg.get('Docente Sostituto')
    d_ass_orig = reg.get('Docente Assente')
    cls_reg = reg.get('Classe')
    if sost_nome and is_docente_assente_in_ora(sost_nome, g_reg, o_reg):
        conflitti_attivi.append({
            'Giorno': g_reg,
            'Ora': o_reg,
            'Classe': cls_reg,
            'Docente Assente Iniziale': d_ass_orig,
            'Supplente Assente': sost_nome
        })

if conflitti_attivi:
    dettagli_conf = [
        f"• **{c['Giorno']} ({c['Ora'].split(' ')[0]})**: Classe {c['Classe']} - Il supplente **{c['Supplente Assente']}** risulta ora **ASSENTE**! (Sostituiva *{c['Docente Assente Iniziale']}*)"
        for c in conflitti_attivi
    ]
    st.error(
        f"🚨 **ALLERTA CRITICA ({len(conflitti_attivi)} CONFLITTO/I RILEVATO/I):** Ci sono docenti assegnati in supplenza che risultano **ASSENTI**!\n\n"
        + "\n".join(dettagli_conf)
        + "\n\n👉 *Vai nel* ***TAB 2 (Quadro Ore Scoperte)*** *per riassegnare un nuovo sostituto a questa/e classe/i!*"
    )

##### TABS PRINCIPALI DELL'INTERFACCIA
tab_assenze, tab_sostituzioni, tab_registro = st.tabs([
    "📋 1. Inserimento Assenze del Giorno",
    "🎯 2. Quadro Ore Scoperte e Assegnazione Sostituti",
    "📊 3. Registro e Report Giornaliero"
])

##### ==============================================================================
##### TAB 1: INSERIMENTO ASSENZE MULTI-DOCENTE
##### ==============================================================================
with tab_assenze:
    if tot_scop_g > 0 and in_sosp_g == 0 and confl_g == 0:
        st.success(f"🎉 **TUTTE LE CLASSI SONO COPERTE PER {giorno_selezionato.upper()}!** Tutte le {tot_scop_g} ore da sostituire hanno un docente assegnato.")

    st.markdown(f"### 📋 Registrazione Assenze e Permessi per **{giorno_selezionato}**")
    st.write("Inserisci **tutti i docenti assenti della giornata** prima di assegnare le supplenze. L'algoritmo escluderà automaticamente questi docenti dalle disponibilità per evitare doppi incarichi.")

    col_add1, col_add2, col_add3 = st.columns([2, 2, 3])

    docenti_disponibili_list = sorted(df_schedule['Docente'].astype(str).unique().tolist())

    with col_add1:
        doc_ass_sel = st.selectbox("Seleziona Docente Assente", docenti_disponibili_list, key="sel_doc_ass")

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
        ore_classe_doc = [s for s in ore_lezione_doc if ore_dict[s].upper() not in ['DISP', 'D', 'DISPOSIZIONE']]
        ore_disp_doc = [s for s in ore_lezione_doc if ore_dict[s].upper() in ['DISP', 'D', 'DISPOSIZIONE']]
        
        supplenze_gia_assegnate = [
            r for r in st.session_state.registro
            if r.get('Giorno') == giorno_selezionato and r.get('Docente Sostituto') == doc_ass_sel
        ]
        
        if tipo_assenza == "🔴 Tutto il Giorno":
            ore_selezionate_ass = list(ore_lezione_doc)
            if not ore_lezione_doc:
                st.warning(f"Nessuna lezione propria in orario per **{doc_ass_sel}** il **{giorno_selezionato}**.")
            elif not ore_classe_doc:
                st.info(f"Il docente **{doc_ass_sel}** il **{giorno_selezionato}** non ha classi proprie da sostituire" + (f" (ha {len(ore_disp_doc)} ora/e a disposizione)." if ore_disp_doc else "."))
            else:
                dettaglio_list = [f"• **{s}**: Classe `{ore_dict[s]}`" for s in ore_classe_doc]
                msg_disp_note = f"\n\n*(Nota: {len(ore_disp_doc)} ora/e a disposizione non richiedono sostituto e sono escluse da questa lista)*" if ore_disp_doc else ""
                st.info(f"Verranno inserite le **{len(ore_classe_doc)} ore da sostituire** del docente per **{giorno_selezionato}**:\n\n" + "\n".join(dettaglio_list) + msg_disp_note)
        else:
            if not ore_lezione_doc:
                st.warning("Nessuna lezione trovata a orario per questo docente.")
                ore_selezionate_ass = []
            else:
                ore_selezionate_ass = st.multiselect(
                    "Seleziona le ore di Permesso / Assenza:",
                    options=ore_lezione_doc,
                    default=ore_lezione_doc,
                    format_func=lambda s: f"{s} (Classe {ore_dict[s]})" if ore_dict[s].upper() not in ['DISP', 'D', 'DISPOSIZIONE'] else f"{s} (DISP - no sostituto)"
                )

        if supplenze_gia_assegnate:
            dettagli_supp = [
                f"• **{s['Ora']}**: Classe `{s['Classe']}` (in sostituzione di *{s['Docente Assente']}*)"
                for s in supplenze_gia_assegnate
            ]
            st.error(
                f"⚠️ **ATTENZIONE:** Il docente **{doc_ass_sel}** è già stato segnato come **SUPPLENTE** per **{len(supplenze_gia_assegnate)} lezione/i** il **{giorno_selezionato}**:\n\n"
                + "\n".join(dettagli_supp) +
                "\n\n🚨 *Se confermi l'assenza, questa/e supplenza/e risulterà/anno scoperta/e e dovrai riassegnarla/e nel TAB 2!*"
            )

    if st.button("➕ Aggiungi Docente all'Elenco Assenti del Giorno", type="primary"):
        gia_presente = False
        for item in st.session_state.assenze_per_giorno[giorno_selezionato]:
            if item['Docente'] == doc_ass_sel:
                gia_presente = True
                break
                
        if gia_presente:
            st.error(f"⚠️ {doc_ass_sel} è già stato inserito nell'elenco degli assenti per {giorno_selezionato}.")
        elif not ore_selezionate_ass and tipo_assenza != "🔴 Tutto il Giorno":
            st.error("Seleziona almeno un'ora di permesso/assenza.")
        else:
            st.session_state.assenze_per_giorno[giorno_selezionato].append({
                'Docente': doc_ass_sel,
                'Materia': str(r_info.get('Materia', '')),
                'Indirizzo': str(r_info.get('Indirizzo', '')),
                'Tipo': tipo_assenza,
                'Ore': ore_selezionate_ass
            })
            if gsheets_connected:
                save_data_to_gsheets()
            st.success(f"Aggiunto **{doc_ass_sel}** all'elenco assenti!")
            st.rerun()

    st.markdown("---")
    st.subheader(f"📑 Elenco Docenti Assenti Confermati per {giorno_selezionato}")

    if st.session_state.assenze_per_giorno[giorno_selezionato]:
        th1, th2, th3, th4, th5, th6 = st.columns([2.2, 1.8, 1.5, 1.8, 1.8, 0.8])
        th1.markdown("**Docente Assente**")
        th2.markdown("**Materia**")
        th3.markdown("**Indirizzo**")
        th4.markdown("**Tipologia Assenza**")
        th5.markdown("**Ore Coinvolte**")
        th6.markdown("**Azione**")
        st.markdown("---")
        
        for idx, item in enumerate(list(st.session_state.assenze_per_giorno[giorno_selezionato])):
            tc1, tc2, tc3, tc4, tc5, tc6 = st.columns([2.2, 1.8, 1.5, 1.8, 1.8, 0.8])
            tc1.markdown(f"👤 **{item['Docente']}**")
            tc2.write(item['Materia'])
            ind_val = item.get('Indirizzo', '')
            if not ind_val:
                r_temp = df_schedule[df_schedule['Docente'] == item['Docente']]
                if len(r_temp) > 0:
                    ind_val = str(r_temp.iloc[0].get('Indirizzo', ''))
            tc3.write(ind_val)
            tc4.write(item['Tipo'])
            
            r_temp_tab1 = df_schedule[df_schedule['Docente'] == item['Docente']]
            r_info_tab1 = r_temp_tab1.iloc[0] if len(r_temp_tab1) > 0 else {}
            ore_classe_conf = [
                o for o in item['Ore'] 
                if str(r_info_tab1.get(f"{giorno_selezionato}_{o}", '')).strip().upper() not in ['DISP', 'D', 'DISPOSIZIONE', 'NAN', 'NONE', '']
            ]
            ore_str = ", ".join([o.split(" ")[0] for o in ore_classe_conf]) if ore_classe_conf else "Nessuna classe da sostituire"
            
            tc5.write(ore_str)
            if tc6.button("❌", key=f"btn_remove_inline_tab1_{idx}_{item['Docente']}", help=f"Rimuovi {item['Docente']} dagli assenti"):
                doc_removed = item['Docente']
                st.session_state.assenze_per_giorno[giorno_selezionato] = [
                    x for x in st.session_state.assenze_per_giorno[giorno_selezionato] if x['Docente'] != doc_removed
                ]
                st.session_state.registro = [
                    r for r in st.session_state.registro 
                    if not (r.get('Giorno') == giorno_selezionato and r.get('Docente Assente') == doc_removed)
                ]
                if gsheets_connected:
                    save_data_to_gsheets()
                st.success(f"Rimesso in servizio **{doc_removed}** (rimosso dall'elenco assenti)!")
                st.rerun()

        st.markdown("---")
        c_del1, c_del2 = st.columns([3, 1])
        with c_del2:
            if st.button("🗑️ Svuota Elenco Assenti del Giorno"):
                st.session_state.assenze_per_giorno[giorno_selezionato] = []
                if gsheets_connected:
                    save_data_to_gsheets()
                st.rerun()
    else:
        st.info("Nessun docente assente registrato per oggi. Seleziona i docenti in alto e clicca su 'Aggiungi'.")

    st.markdown("---")
    st.subheader("📜 Quadro Generale Assenze di Tutta la Settimana")
    tutte_assenze_settimana = []
    for g in GIORNI:
        for item in st.session_state.assenze_per_giorno.get(g, []):
            r_temp = df_schedule[df_schedule['Docente'] == item['Docente']]
            r_info_temp = r_temp.iloc[0] if len(r_temp) > 0 else {}
            
            ore_classe_sett = [
                o for o in item['Ore'] 
                if str(r_info_temp.get(f"{g}_{o}", '')).strip().upper() not in ['DISP', 'D', 'DISPOSIZIONE', 'NAN', 'NONE', '']
            ]
            
            ore_str = ", ".join([o.split(" ")[0] for o in ore_classe_sett]) if ore_classe_sett else "Nessuna classe da sostituire"
            
            ind_val = item.get('Indirizzo', '')
            if not ind_val and len(r_temp) > 0:
                ind_val = str(r_temp.iloc[0].get('Indirizzo', ''))
                
            tutte_assenze_settimana.append({
                'Giorno': g,
                'Docente Assente': item['Docente'],
                'Materia': item['Materia'],
                'Indirizzo': ind_val,
                'Tipologia': item['Tipo'],
                "Ore Coinvolte dall'Assenza": ore_str
            })
            
    if tutte_assenze_settimana:
        df_tutte_ass = pd.DataFrame(tutte_assenze_settimana)
        st.dataframe(df_tutte_ass, use_container_width=True)
    else:
        st.caption("Nessuna assenza registrata al momento per alcun giorno della settimana.")


##### ==============================================================================
##### TAB 2: QUADRO ORE SCOPERTE E ASSEGNAZIONE SOSTITUTI
##### ==============================================================================
with tab_sostituzioni:
    st.markdown(f"### 🎯 Quadro Ore Scoperte e Ricerca Sostituti ({giorno_selezionato})")

    docenti_assenti_per_ora = {slot: set() for slot in ORE}
    for item in st.session_state.assenze_per_giorno[giorno_selezionato]:
        d_nome = item['Docente']
        for slot in ORE:
            if is_docente_assente_in_ora(d_nome, giorno_selezionato, slot):
                docenti_assenti_per_ora[slot].add(d_nome)
            
    docenti_sostituti_occupati_per_ora = {slot: set() for slot in ORE}
    for reg in st.session_state.registro:
        if reg.get('Giorno') == giorno_selezionato:
            s_ora = reg.get('Ora')
            s_nome = reg.get('Docente Sostituto')
            if s_nome and not is_docente_assente_in_ora(s_nome, giorno_selezionato, s_ora):
                docenti_sostituti_occupati_per_ora[s_ora].add(s_nome)

    classi_scoperte_lista = []
    ore_disp_assenti_lista = []

    for item in st.session_state.assenze_per_giorno[giorno_selezionato]:
        d_nome = item['Docente']
        r_doc = df_schedule[df_schedule['Docente'] == d_nome]
        r_info = r_doc.iloc[0] if len(r_doc) > 0 else {}
        d_mat = str(r_info.get('Materia', 'Generale'))
        
        ore_effettive_doc = item['Ore'] if item.get('Tipo') != "🔴 Tutto il Giorno" else ORE
        
        for slot in ore_effettive_doc:
            slot_key = f"{giorno_selezionato}_{slot}"
            cls_val = str(r_info.get(slot_key, '')).strip()
            
            sostituto_assegnato = None
            for reg in st.session_state.registro:
                if reg.get('Giorno') == giorno_selezionato and reg.get('Ora') == slot and reg.get('Docente Assente') == d_nome:
                    sostituto_assegnato = reg.get('Docente Sostituto')
                    break
                    
            if cls_val and cls_val.upper() != 'NAN' and cls_val != '':
                if cls_val.upper() in ['DISP', 'D', 'DISPOSIZIONE']:
                    ore_disp_assenti_lista.append({
                        'Docente Assente': d_nome,
                        'Materia': d_mat,
                        'Ora': slot,
                        'Stato': 'Ora a Disposizione (Nessuna classe da coprire)'
                    })
                else:
                    stato_sost = "🔴 IN SOSPESO"
                    if sostituto_assegnato:
                        if is_docente_assente_in_ora(sostituto_assegnato, giorno_selezionato, slot):
                            stato_sost = f"🚨 CONFLITTO: {sostituto_assegnato} (ASSENTE!)"
                        else:
                            stato_sost = sostituto_assegnato

                    classi_scoperte_lista.append({
                        'Docente Assente': d_nome,
                        'Materia': d_mat,
                        'Ora': slot,
                        'Classe / Slot': cls_val,
                        'Sostituto Assegnato': stato_sost
                    })

    if not st.session_state.assenze_per_giorno[giorno_selezionato]:
        st.warning("⚠️ Nessun docente assente inserito nel TAB 1. Torna al primo passaggio per registrare le assenze.")
    elif not classi_scoperte_lista:
        st.info("Tutte le assenze inserite riguardano ore libere o ore a disposizione (DISP) per le quali non serve un supplente.")
        if ore_disp_assenti_lista:
            st.caption("ℹ️ Le ore DISP dei docenti assenti non richiedono la ricerca di un sostituto perché non c'è una classe da coprire.")
    else:
        totale_scoperte = len(classi_scoperte_lista)
        in_sospeso_cnt = sum(1 for r in classi_scoperte_lista if r['Sostituto Assegnato'] == "🔴 IN SOSPESO")
        conflitti_cnt = sum(1 for r in classi_scoperte_lista if "🚨 CONFLITTO" in r['Sostituto Assegnato'])
        coperte_cnt = totale_scoperte - in_sospeso_cnt - conflitti_cnt

        if in_sospeso_cnt == 0 and conflitti_cnt == 0:
            st.success(f"🎉 **TUTTE LE CLASSI SONO COPERTE!** Tutte le **{totale_scoperte}** ore scoperte per **{giorno_selezionato}** hanno un sostituto regolarmente assegnato.")
            st.toast(f"🎉 Tutte le {totale_scoperte} classi per {giorno_selezionato} sono coperte!")
        else:
            st.info(f"📊 **Stato Copertura Classi ({giorno_selezionato}):** **{coperte_cnt}/{totale_scoperte}** ore coperte | 🔴 **{in_sospeso_cnt}** in sospeso" + (f" | 🚨 **{conflitti_cnt}** in conflitto" if conflitti_cnt > 0 else ""))

        st.markdown("#### 📌 Tabellone Riassuntivo delle Ore da Coprire")
        
        th1, th2, th3, th4, th5, th6 = st.columns([1.2, 0.8, 2.0, 2.0, 2.2, 1.0])
        th1.markdown("**Ora**")
        th2.markdown("**Classe**")
        th3.markdown("**Docente Assente**")
        th4.markdown("**Materia**")
        th5.markdown("**Sostituto Assegnato**")
        th6.markdown("**Azione**")
        st.markdown("---")
        
        for idx_row, row_s in enumerate(classi_scoperte_lista):
            tc1, tc2, tc3, tc4, tc5, tc6 = st.columns([1.2, 0.8, 2.0, 2.0, 2.2, 1.0])
            tc1.write(row_s['Ora'].split(' ')[0])
            tc2.write(f"**{row_s['Classe / Slot']}**")
            tc3.write(row_s['Docente Assente'])
            tc4.write(row_s['Materia'])
            
            sost_val = row_s['Sostituto Assegnato']
            if "🚨 CONFLITTO" in sost_val:
                tc5.markdown(f"**{sost_val}**")
                tc6.write("⚠️ Riassegna")
            elif sost_val != "🔴 IN SOSPESO":
                tc5.markdown(f"🟢 **{sost_val}**")
                if tc6.button("❌", key=f"btn_del_inline_{idx_row}_{row_s['Ora']}", help=f"Rimuovi sostituto {sost_val}"):
                    d_ass_del = row_s['Docente Assente']
                    ora_del = row_s['Ora']
                    st.session_state.registro = [
                        reg for reg in st.session_state.registro 
                        if not (reg.get('Giorno') == giorno_selezionato and reg.get('Ora') == ora_del and reg.get('Docente Assente') == d_ass_del)
                    ]
                    if gsheets_connected:
                        save_data_to_gsheets()
                    st.success(f"Rimosso sostituto **{sost_val}** per la classe {row_s['Classe / Slot']}!")
                    st.rerun()
            else:
                tc5.markdown("🔴 *IN SOSPESO*")
                tc6.write("—")
        
        if ore_disp_assenti_lista:
            st.info(f"💡 **Nota sulle ore DISP:** {len(ore_disp_assenti_lista)} ora/e a disposizione (DISP) di docenti assenti sono state automaticamente escluse da questa lista perché non c'è una classe da coprire.")
        
        st.markdown("---")
        st.subheader("🔍 Assegnazione Sostituto per un'Ora Scoperta")
        
        opzioni_scoperte = []
        for idx, row_s in enumerate(classi_scoperte_lista):
            stato_icon = "🟢" if ("🟢" in row_s['Sostituto Assegnato'] or (row_s['Sostituto Assegnato'] != "🔴 IN SOSPESO" and "🚨" not in row_s['Sostituto Assegnato'])) else ("🚨" if "🚨" in row_s['Sostituto Assegnato'] else "🔴")
            opzioni_scoperte.append(f"{stato_icon} {row_s['Ora']} | Assente: {row_s['Docente Assente']} | Classe: {row_s['Classe / Slot']} | Sostituto: {row_s['Sostituto Assegnato']}")
            
        idx_scoperta_sel = st.selectbox("Seleziona la lezione da coprire:", range(len(opzioni_scoperte)), format_func=lambda i: opzioni_scoperte[i])
        
        target_slot = classi_scoperte_lista[idx_scoperta_sel]
        docente_assente_target = target_slot['Docente Assente']
        ora_target = target_slot['Ora']
        classe_target = target_slot['Classe / Slot']
        materia_target = target_slot['Materia']
        sostituto_corrente = target_slot['Sostituto Assegnato']
        
        if "🚨 CONFLITTO" in sostituto_corrente:
            st.error(f"📍 **Dettagli Lezione:** `{giorno_selezionato}`, `{ora_target}` | **Docente Assente:** `{docente_assente_target}` | **Classe:** `{classe_target}` | **Materia:** `{materia_target}` | {sostituto_corrente}")
        else:
            st.info(f"📍 **Dettagli Lezione:** `{giorno_selezionato}`, `{ora_target}` | **Docente Assente:** `{docente_assente_target}` | **Classe:** `{classe_target}` | **Materia:** `{materia_target}`" + (f" | 🟢 **Sostituto:** `{sostituto_corrente}`" if sostituto_corrente != "🔴 IN SOSPESO" else ""))
        
        esclusi_assenti = docenti_assenti_per_ora.get(ora_target, set())
        esclusi_sostituti = docenti_sostituti_occupati_per_ora.get(ora_target, set())
        tot_esclusi = esclusi_assenti.union(esclusi_sostituti)
        
        st.caption(f"🛡️ **Sicurezza Anti-Sovrapposizione ({ora_target}):** {len(tot_esclusi)} docenti esclusi (di cui {len(esclusi_assenti)} assenti e {len(esclusi_sostituti)} già in supplenza).")
        
        slot_key_target = f"{giorno_selezionato}_{ora_target}"
        indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_target if classe_target != 'DISP' else '1a', ('ITE', 'Istituto Tecnico Economico'))
        
        all_cands = []
        
        for idx, r in df_schedule.iterrows():
            d_nome = str(r['Docente']).strip()
            
            if d_nome in tot_esclusi or is_docente_assente_in_ora(d_nome, giorno_selezionato, ora_target):
                continue
            
            in_servizio_giorno = False
            for slot_check in ORE:
                v_check = str(r.get(f"{giorno_selezionato}_{slot_check}", '')).strip().upper()
                if v_check and v_check != 'NAN' and v_check != 'NONE':
                    in_servizio_giorno = True
                    break
            
            if not in_servizio_giorno:
                continue
                
            d_mat = str(r.get('Materia', '')).strip()
            d_ind = str(r.get('Indirizzo', '')).strip()
            d_cdc_list = [c.strip() for c in str(r.get('CdC', '')).split(',') if c.strip()]
            
            is_cdc = (classe_target in d_cdc_list) if (classe_target and classe_target != 'DISP') else False
            is_ind = (d_ind == indirizzo_codice)
            is_mat = (d_mat == materia_target)
            
            val_ora = str(r.get(slot_key_target, '')).strip()
            val_ora_upper = val_ora.upper()
            
            is_disp = val_ora_upper in ['D', 'DISP', 'DISPOSIZIONE']
            
            if val_ora and not is_disp and val_ora_upper != 'NAN' and (val_ora in CLASSES_INFO or val_ora_upper not in ['NAN', 'NONE', '']):
                if val_ora in CLASSES_INFO or any(c in val_ora for c in CLASSES_INFO):
                    continue
            
            if is_disp:
                if is_cdc:
                    rank = 1
                    prio = "1. DISP | Stesso CdC"
                elif is_ind and is_mat:
                    rank = 2
                    prio = "2. DISP | Stesso Indirizzo - Stessa Materia"
                elif is_ind:
                    rank = 3
                    prio = "3. DISP | Stesso Indirizzo - Altra Materia"
                elif is_mat:
                    rank = 4
                    prio = "4. DISP | Altro Indirizzo - Stessa Materia"
                else:
                    rank = 5
                    prio = "5. DISP | Altro Indirizzo - Altra Materia"
                    
                stato_desc = "DISPOSIZIONE"
                tipo_code = "DISP"
            else:
                ora_idx = ORE.index(ora_target) if ora_target in ORE else 0
                
                has_before = any(
                    str(r.get(f"{giorno_selezionato}_{ORE[i]}", '')).strip().upper() not in ['', 'NAN', 'NONE']
                    for i in range(0, ora_idx)
                )
                has_after = any(
                    str(r.get(f"{giorno_selezionato}_{ORE[i]}", '')).strip().upper() not in ['', 'NAN', 'NONE']
                    for i in range(ora_idx + 1, len(ORE))
                )
                
                if has_before and has_after:
                    tipo_extra = "Ora Buca"
                elif has_after:
                    tipo_extra = "Entrata Anticipata (+1h)"
                elif has_before:
                    tipo_extra = "Uscita Posticipata (+1h)"
                else:
                    tipo_extra = "Libero / Fuori Servizio"
                
                if is_cdc:
                    rank = 6
                    prio = f"6. Extra ({tipo_extra}) | Stesso CdC"
                elif is_ind and is_mat:
                    rank = 7
                    prio = f"7. Extra ({tipo_extra}) | Stesso Indirizzo - Stessa Materia"
                elif is_ind:
                    rank = 8
                    prio = f"8. Extra ({tipo_extra}) | Stesso Indirizzo - Altra Materia"
                elif is_mat:
                    rank = 9
                    prio = f"9. Extra ({tipo_extra}) | Altro Indirizzo - Stessa Materia"
                else:
                    rank = 10
                    prio = f"10. Extra ({tipo_extra}) | Altro Indirizzo - Altra Materia"
                    
                stato_desc = tipo_extra
                tipo_code = "EXTRA"

            all_cands.append({
                'Rank': rank,
                'Docente': d_nome,
                'Materia': d_mat,
                'Indirizzo': d_ind,
                'Stato': stato_desc,
                'CdC': f"Sì ({classe_target})" if is_cdc else "No",
                'Priorità': prio,
                'Tipo': tipo_code
            })

        all_cands.sort(key=lambda x: (x['Rank'], x['Docente']))
        
        if all_cands:
            df_display = pd.DataFrame(all_cands).drop(columns=['Rank', 'Tipo'])
            st.dataframe(df_display, use_container_width=True)
            
            labels_cands = [f"{c['Docente']} | {c['Priorità']} | {c['Stato']}" for c in all_cands]
            scelta_cand_idx = st.selectbox("Scegli il docente da assegnare a questa classe:", range(len(labels_cands)), format_func=lambda i: labels_cands[i])
            
            cand_scelto = all_cands[scelta_cand_idx]
            
            btn_label = "✅ Conferma / Riassegna Sostituto" if "🚨 CONFLITTO" in sostituto_corrente else "✅ Conferma Assegnazione Sostituto"
            if st.button(btn_label, type="primary"):
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
                if gsheets_connected:
                    save_data_to_gsheets()
                st.success(f"Assegnato con successo **{cand_scelto['Docente']}** per la classe **{classe_target}** ({ora_target})!")
                st.rerun()
        else:
            st.error("🔴 Nessun docente disponibile o in ora buca trovato per questo slot tra quelli in servizio.")


##### ==============================================================================
##### TAB 3: REGISTRO E REPORT GIORNALIERO
##### ==============================================================================
with tab_registro:
    st.markdown(f"### 📊 Registro delle Sostituzioni Assegnate per **{giorno_selezionato}**")

    reg_giorno = [r for r in st.session_state.registro if r.get('Giorno') == giorno_selezionato]

    if reg_giorno:
        reg_giorno_sorted = sort_registro_by_day_and_teacher(reg_giorno)
        df_reg_giorno = pd.DataFrame(reg_giorno_sorted)
        
        stati_sost = []
        for r in reg_giorno_sorted:
            s_nome = r.get('Docente Sostituto')
            g_val = r.get('Giorno')
            o_val = r.get('Ora')
            if s_nome and is_docente_assente_in_ora(s_nome, g_val, o_val):
                stati_sost.append(f"🚨 ASSENTE ({s_nome})")
            else:
                stati_sost.append("🟢 Presente")
        df_reg_giorno['Stato Sostituto'] = stati_sost

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
    st.subheader("📜 Storico Completo Sessione (Tutti i Giorni — Ordinato per Giorno e Docente)")
    if st.session_state.registro:
        reg_completo_sorted = sort_registro_by_day_and_teacher(st.session_state.registro)
        df_reg_completo = pd.DataFrame(reg_completo_sorted)
        
        stati_sost_comp = []
        for r in reg_completo_sorted:
            s_nome = r.get('Docente Sostituto')
            g_val = r.get('Giorno')
            o_val = r.get('Ora')
            if s_nome and is_docente_assente_in_ora(s_nome, g_val, o_val):
                stati_sost_comp.append(f"🚨 ASSENTE ({s_nome})")
            else:
                stati_sost_comp.append("🟢 Presente")
        df_reg_completo['Stato Sostituto'] = stati_sost_comp

        st.dataframe(df_reg_completo, use_container_width=True)
        
        csv_completo_data = df_reg_completo.to_csv(index=False).encode('utf-8')
        col_dl1, col_dl2 = st.columns([3, 1])
        with col_dl1:
            st.download_button(
                label="📥 Scarica Report Storico Completo Settimanale (CSV)",
                data=csv_completo_data,
                file_name="sostituzioni_storico_completo_Calvino.csv",
                mime="text/csv"
            )
        with col_dl2:
            if st.button("🗑️ Cancella Tutto il Registro"):
                st.session_state.registro = []
                if gsheets_connected:
                    save_data_to_gsheets()
                st.rerun()
    else:
        st.info("Il registro generale è vuoto.")

    st.markdown("---")
    st.subheader("📥 Importa / Ripristina Storico da File CSV")
    st.write("Puoi ricaricare un file CSV esportato in precedenza per ripristinare tutte le sostituzioni e gli assenti registrati.")
    
    col_imp1, col_imp2 = st.columns([2, 1])
    with col_imp1:
        uploaded_tab_csv = st.file_uploader("Carica File CSV di Registro", type=['csv'], key="tab3_csv_uploader")
    with col_imp2:
        st.markdown("<br>", unsafe_allow_html=True)
        replace_opt = st.checkbox("Sostituisci il registro attuale (cancella esistenti)", value=True)
        
    if uploaded_tab_csv is not None:
        if st.button("🔄 Importa Dati da CSV", type="primary", key="btn_import_tab3"):
            if import_registro_from_csv(uploaded_tab_csv, replace_existing=replace_opt):
                st.rerun()
