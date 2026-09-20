import streamlit as st
import pandas as pd
import io
import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Attempt to import GSheetsConnection
try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False

st.set_page_config(
    page_title="Gestione Sostituzioni - I.I.S. Italo Calvino",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a237e !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

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
    '1ª ora (08:00)',
    '2ª ora (08:55)',
    '3ª ora (10:00)',
    '4ª ora (10:55)',
    '5ª ora (12:00)',
    '6ª ora (12:55)',
    '7ª ora (14:00)'
]

def clean_pdf_text(text):
    if not text:
        return ""
    text = str(text)
    emojis_and_symbols = ['🔴', '🟢', '🚨', '📅', '👤', '🏫', '📊', '📋', '🎯', '📥', '🔄', '🗑️', '🎉', '⏳', '🌟', 'ℹ️', '⚠️', '📍', '🛡️', '📌', '📜', '📂', '⚙️', '📥', '🗑️']
    for s in emojis_and_symbols:
        text = text.replace(s, '')
    text = text.replace('ª', 'a').replace('º', 'o').replace('“', '"').replace('”', '"').replace('’', "'").replace('–', '-').replace('—', '-')
    text = text.encode('latin-1', 'replace').decode('latin-1')
    return text.strip()

class CircolarePDF(FPDF):
    def __init__(self, giorno_str, data_str):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.giorno_str = giorno_str
        self.data_str = data_str
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(26, 35, 126) # #1a237e
        self.cell(0, 5, 'ISTITUTO DI ISTRUZIONE SUPERIORE "ITALO CALVINO"', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.set_font('Helvetica', '', 8)
        self.set_text_color(60, 60, 60)
        self.cell(0, 4, 'Via Guido Rossa - 20089 ROZZANO (MI) - Tel. 0257500115', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 4, 'Cod. mecc. MIIS01900L - C.F. 97270410158 - Cod. Fatt. Elettronica: UFSDER', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 4, 'Email: MIIS01900L@istruzione.it - Pec: MIIS01900L@pec.istruzione.it - Web: www.istitutocalvino.edu.it', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.set_draw_color(26, 35, 126)
        self.set_line_width(0.6)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, clean_pdf_text(f"Pagina {self.page_no()} - I.I.S. Italo Calvino - Documento generato il {self.data_str}"), align='C')

def create_circolare_pdf_bytes(giorno, data_str, num_circolare, rows, oggetto_str=""):
    pdf = CircolarePDF(giorno, data_str)
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 8, clean_pdf_text(f"CIRCOLARE N. {num_circolare}" if num_circolare else "CIRCOLARE SOSTITUZIONI DOCENTI"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, clean_pdf_text(f"Oggetto: {oggetto_str}" if oggetto_str else f"Oggetto: Variazioni d'orario e sostituzioni docenti assenti per la giornata di {giorno} ({data_str})"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    
    col_w = [18, 18, 45, 30, 45, 34]
    
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    
    headers = ['Ora', 'Classe', 'Docente Assente', 'Materia', 'Docente Sostituto', 'Tipologia']
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, clean_pdf_text(h), border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 8)
    
    for r in rows:
        ora_val = clean_pdf_text(r.get('Ora', '')).split(' ')[0]
        cls_val = clean_pdf_text(r.get('Classe', ''))
        d_ass_val = clean_pdf_text(r.get('Docente Assente', ''))
        mat_val = clean_pdf_text(r.get('Materia', ''))
        sost_val = clean_pdf_text(r.get('Docente Sostituto', ''))
        tipo_val = clean_pdf_text(r.get('Tipologia Sostituzione', ''))
        
        pdf.cell(col_w[0], 6, ora_val, border=1, align='C')
        pdf.cell(col_w[1], 6, cls_val, border=1, align='C')
        pdf.cell(col_w[2], 6, d_ass_val[:22], border=1, align='L')
        pdf.cell(col_w[3], 6, mat_val[:18], border=1, align='L')
        pdf.cell(col_w[4], 6, sost_val[:22], border=1, align='L')
        pdf.cell(col_w[5], 6, tipo_val[:16], border=1, align='C')
        pdf.ln()
        
    return bytes(pdf.output())

def create_storico_pdf_bytes(data_str, rows):
    pdf = CircolarePDF("Settimanale", data_str)
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 8, clean_pdf_text("REPORT STORICO SETTIMANALE SOSTITUZIONI"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(4)
    
    col_w = [22, 16, 16, 40, 26, 40, 30]
    
    pdf.set_fill_color(26, 35, 126)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8)
    
    headers = ['Giorno', 'Ora', 'Classe', 'Docente Assente', 'Materia', 'Docente Sostituto', 'Tipologia']
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, clean_pdf_text(h), border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 8)
    
    for r in rows:
        g_val = clean_pdf_text(r.get('Giorno', ''))
        ora_val = clean_pdf_text(r.get('Ora', '')).split(' ')[0]
        cls_val = clean_pdf_text(r.get('Classe', ''))
        d_ass_val = clean_pdf_text(r.get('Docente Assente', ''))
        mat_val = clean_pdf_text(r.get('Materia', ''))
        sost_val = clean_pdf_text(r.get('Docente Sostituto', ''))
        tipo_val = clean_pdf_text(r.get('Tipologia Sostituzione', ''))
        
        pdf.cell(col_w[0], 6, g_val[:10], border=1, align='L')
        pdf.cell(col_w[1], 6, ora_val, border=1, align='C')
        pdf.cell(col_w[2], 6, cls_val, border=1, align='C')
        pdf.cell(col_w[3], 6, d_ass_val[:20], border=1, align='L')
        pdf.cell(col_w[4], 6, mat_val[:15], border=1, align='L')
        pdf.cell(col_w[5], 6, sost_val[:20], border=1, align='L')
        pdf.cell(col_w[6], 6, tipo_val[:15], border=1, align='C')
        pdf.ln()
        
    return bytes(pdf.output())

# Helper per accedere al client gspread in modo compatibile sia con le vecchie che con le nuove versioni di st-gsheets-connection
def get_gsheets_client(conn):
    if conn is None:
        return None
    try:
        if hasattr(conn, '_instance') and hasattr(conn._instance, '_client') and conn._instance._client is not None:
            return conn._instance._client
    except Exception:
        pass
    try:
        if hasattr(conn, '_client') and conn._client is not None:
            return conn._client
    except Exception:
        pass
    try:
        if hasattr(conn, 'client') and conn.client is not None:
            return conn.client
    except Exception:
        pass
    return None

def safe_gsheets_read(conn, worksheet_name):
    try:
        client = get_gsheets_client(conn)
        if client is not None and hasattr(conn, 'url') and conn.url:
            spr = client.open_by_url(conn.url)
            target_clean = worksheet_name.strip().lower()
            matched_ws = None
            for ws in spr.worksheets():
                if ws.title.strip().lower() == target_clean:
                    matched_ws = ws
                    break
            
            if matched_ws is not None:
                df = get_as_dataframe(matched_ws, evaluate_formulas=True)
                if df is not None and not df.empty:
                    df = df.dropna(how='all')
                    return df
            return pd.DataFrame()
        else:
            if hasattr(conn, 'read'):
                return conn.read(worksheet=worksheet_name, ttl=0)
    except Exception:
        pass
    return pd.DataFrame()

def safe_gsheets_update(conn, worksheet_name, df_data):
    try:
        client = get_gsheets_client(conn)
        if client is not None and hasattr(conn, 'url') and conn.url:
            spr = client.open_by_url(conn.url)
            target_clean = worksheet_name.strip().lower()
            matched_ws = None
            for ws in spr.worksheets():
                if ws.title.strip().lower() == target_clean:
                    matched_ws = ws
                    break
            
            if matched_ws is None:
                try:
                    matched_ws = spr.add_worksheet(title=worksheet_name, rows=100, cols=20)
                except Exception as e_add:
                    for ws in spr.worksheets():
                        if ws.title.strip().lower() == target_clean:
                            matched_ws = ws
                            break
                    if matched_ws is None:
                        raise e_add

            matched_ws.clear()
            if df_data is None or df_data.empty:
                cols = list(df_data.columns) if hasattr(df_data, 'columns') and len(df_data.columns) > 0 else []
                empty_df = pd.DataFrame(columns=cols)
                set_with_dataframe(matched_ws, empty_df)
            else:
                set_with_dataframe(matched_ws, df_data)
            return True, None
        else:
            if hasattr(conn, 'update'):
                conn.update(worksheet=worksheet_name, data=df_data)
                return True, None
            return False, "Impossibile accedere al client Google Fogli."
    except Exception as e:
        try:
            if hasattr(conn, 'update'):
                conn.update(worksheet=worksheet_name, data=df_data)
                return True, None
        except Exception as e2:
            pass
        return False, str(e)

st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze - Modulo Gestione Settimanale e Storico Assenze (A.S. 2026/2027 - v32)")

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

# Session State Initialization
if 'assenze_per_giorno' not in st.session_state:
    st.session_state.assenze_per_giorno = {g: [] for g in GIORNI}
if 'registro' not in st.session_state:
    st.session_state.registro = []
if 'gsheets_loaded' not in st.session_state:
    st.session_state.gsheets_loaded = False

# Google Sheets connection setup
conn = None
gsheets_connected = False
if HAS_GSHEETS:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        gsheets_connected = True
    except Exception as e:
        gsheets_connected = False
        st.session_state.gsheets_last_error = str(e)

def load_data_from_gsheets():
    if not gsheets_connected or conn is None:
        return False, "Google Sheets non connesso."
    try:
        df_ass = safe_gsheets_read(conn, "Assenze")
        if not df_ass.empty:
            assenze_dict = {g: [] for g in GIORNI}
            for _, r in df_ass.iterrows():
                g = str(r.get('Giorno', '')).strip()
                doc = str(r.get('Docente', '')).strip()
                mat = str(r.get('Materia', '')).strip()
                ind = str(r.get('Indirizzo', '')).strip()
                tipo = str(r.get('Tipo', '')).strip()
                ore_raw = str(r.get('Ore', '')).strip()
                
                if g in GIORNI and doc:
                    ore_list = [o.strip() for o in ore_raw.split(',') if o.strip()]
                    ore_full = [o for o in ORE if any(o.startswith(x) or x in o for x in ore_list)] if ore_list else ORE
                    assenze_dict[g].append({
                        'Docente': doc,
                        'Materia': mat,
                        'Indirizzo': ind,
                        'Tipo': tipo,
                        'Ore': ore_full if ore_full else ORE
                    })
            st.session_state.assenze_per_giorno = assenze_dict

        df_reg = safe_gsheets_read(conn, "Registro")
        if not df_reg.empty:
            reg_list = []
            for _, r in df_reg.iterrows():
                reg_list.append({
                    'Giorno': str(r.get('Giorno', '')).strip(),
                    'Ora': str(r.get('Ora', '')).strip(),
                    'Docente Assente': str(r.get('Docente Assente', '')).strip(),
                    'Classe': str(r.get('Classe', '')).strip(),
                    'Materia': str(r.get('Materia', '')).strip(),
                    'Docente Sostituto': str(r.get('Docente Sostituto', '')).strip(),
                    'Tipologia Sostituzione': str(r.get('Tipologia Sostituzione', '')).strip(),
                    'Priorità Applicata': str(r.get('Priorità Applicata', '')).strip()
                })
            st.session_state.registro = reg_list
        return True, None
    except Exception as e:
        return False, str(e)

def save_data_to_gsheets():
    if not gsheets_connected or conn is None:
        return False
    try:
        rows_ass = []
        for g, items in st.session_state.assenze_per_giorno.items():
            for item in items:
                ore_short = [o.split(' ')[0] for o in item.get('Ore', [])]
                rows_ass.append({
                    'Giorno': g,
                    'Docente': item.get('Docente', ''),
                    'Materia': item.get('Materia', ''),
                    'Indirizzo': item.get('Indirizzo', ''),
                    'Tipo': item.get('Tipo', ''),
                    'Ore': ", ".join(ore_short)
                })
        df_ass_out = pd.DataFrame(rows_ass)
        if df_ass_out.empty:
            df_ass_out = pd.DataFrame(columns=['Giorno', 'Docente', 'Materia', 'Indirizzo', 'Tipo', 'Ore'])

        df_reg_out = pd.DataFrame(st.session_state.registro)
        if df_reg_out.empty:
            df_reg_out = pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Priorità Applicata'])

        success_a, err_a = safe_gsheets_update(conn, "Assenze", df_ass_out)
        success_r, err_r = safe_gsheets_update(conn, "Registro", df_reg_out)
        return success_a and success_r
    except Exception as e:
        st.session_state.gsheets_last_error = str(e)
        return False

if gsheets_connected and not st.session_state.gsheets_loaded:
    success_init, err_init = load_data_from_gsheets()
    if success_init:
        st.session_state.gsheets_loaded = True

def is_docente_assente_in_ora(docente, giorno, ora):
    if not docente or 'assenze_per_giorno' not in st.session_state:
        return False
    assenze = st.session_state.assenze_per_giorno.get(giorno, [])
    for item in assenze:
        if item.get('Docente') == docente:
            if item.get('Tipo') == "🔴 Tutto il Giorno":
                return True
            if ora in item.get('Ore', []):
                return True
    return False

# Sidebar Navigation
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    if gsheets_connected:
        st.success("🟢 Google Fogli Connesso")
        if st.button("🔄 Sincronizza Ora da Cloud"):
            s_ok, s_err = load_data_from_gsheets()
            if s_ok:
                st.success("Dati aggiornati da Google Fogli!")
                st.rerun()
            else:
                st.error(f"Errore sincronizzazione: {s_err}")
    else:
        st.warning("🔴 Google Fogli non connesso (uso locale in memoria).")

    st.markdown("---")
    st.subheader("📂 Caricamento Orario Docenti")
    uploaded_file = st.file_uploader("Carica File CSV / Excel dell'Orario Generale:", type=['csv', 'xlsx', 'xls'])

    df_schedule = pd.DataFrame()
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_schedule = pd.read_csv(uploaded_file)
                except Exception:
                    df_schedule = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                df_schedule = pd.read_excel(uploaded_file)
            st.success(f"Orario caricato con successo ({len(df_schedule)} docenti)!")
        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")

    st.markdown("---")
    st.subheader("🗓️ Selezione Giorno di Lavoro")
    giorno_selezionato = st.selectbox(
        "Seleziona il Giorno:",
        GIORNI,
        index=0,
        key="main_giorno_selectbox"
    )

    # Conteggio sintetico e avviso
    scoperte_per_giorno = {}
    for g_check in GIORNI:
        scoperte_g = 0
        assenze_g = st.session_state.assenze_per_giorno.get(g_check, [])
        for item in assenze_g:
            d_name = item['Docente']
            if not df_schedule.empty and 'Docente' in df_schedule.columns:
                r_doc = df_schedule[df_schedule['Docente'] == d_name]
                r_info = r_doc.iloc[0] if len(r_doc) > 0 else {}
                ore_eff = item['Ore'] if item.get('Tipo') != "🔴 Tutto il Giorno" else ORE
                for slot in ore_eff:
                    cls_v = str(r_info.get(f"{g_check}_{slot}", '')).strip()
                    if cls_v and cls_v.upper() not in ['NAN', '', 'NONE', 'DISP', 'D', 'DISPOSIZIONE']:
                        sost_exists = any(
                            reg.get('Giorno') == g_check and reg.get('Ora') == slot and reg.get('Docente Assente') == d_name and reg.get('Docente Sostituto')
                            for reg in st.session_state.registro
                        )
                        if not sost_exists:
                            scoperte_g += 1
        scoperte_per_giorno[g_check] = scoperte_g

    st.markdown("#### 📊 Riepilogo Ore Scoperte Settimanali")
    for g_check in GIORNI:
        cnt = scoperte_per_giorno[g_check]
        st.write(f"• **{g_check}**: " + (f"🔴 `{cnt} ora/e scoperte`" if cnt > 0 else "🟢 `Tutto coperto`"))

    altri_giorni = [g for g in GIORNI if g != giorno_selezionato and scoperte_per_giorno[g] > 0]
    if altri_giorni:
        st.warning(f"⚠️ **ALTRI GIORNI DA COPRIRE:** Ci sono ancora classi scoperte in: **{', '.join(altri_giorni)}**")

# Controllo conflitti attivi
conflitti_attivi = []
for reg in st.session_state.registro:
    g_reg = reg.get('Giorno')
    o_reg = reg.get('Ora')
    s_reg = reg.get('Docente Sostituto')
    if s_reg and is_docente_assente_in_ora(s_reg, g_reg, o_reg):
        conflitti_attivi.append({
            'Giorno': g_reg,
            'Ora': o_reg,
            'Classe': reg.get('Classe'),
            'Supplente Assente': s_reg,
            'Docente Assente Iniziale': reg.get('Docente Assente')
        })

if conflitti_attivi:
    dettagli_conf = [
        f"• **{c['Giorno']} ({c['Ora'].split(' ')[0]})**: Classe {c['Classe']} - Il supplente **{c['Supplente Assente']}** risulta ora **ASSENTE**! (Sostituiva *{c['Docente Assente Iniziale']}*)"
        for c in conflitti_attivi
    ]
    st.error(
        f"🚨 **ALLERTA CRITICA ({len(conflitti_attivi)} CONFLITTO/I RILEVATO/I):** Ci sono docenti assegnati in supplenza che risultano **ASSENTI**!\n\n" + "\n".join(dettagli_conf) + "\n\n👉 *Vai nel* ***TAB 2 (Quadro Ore Scoperte)*** *per riassegnare un nuovo sostituto a questa/e classe/i!*"
    )

# Dialog Pop-up di conferma assegnazione sostituto
if hasattr(st, 'dialog'):
    @st.dialog("⚠️ Conferma Assegnazione Sostituto")
    def confirm_sostituto_dialog(cand_scelto, giorno_selezionato, ora_target, docente_assente_target, classe_target, materia_target, gsheets_flag):
        st.markdown(f"### Confermi l'assegnazione di **{cand_scelto['Docente']}**?")
        st.markdown(f"""
        * 📅 **Giorno:** `{giorno_selezionato}`
        * ⏱️ **Ora:** `{ora_target}`
        * 🏫 **Classe:** `{classe_target}`
        * 📚 **Materia:** `{materia_target}`
        * 👤 **Docente Assente:** `{docente_assente_target}`
        * 🟢 **Docente Sostituto:** **{cand_scelto['Docente']}** ({cand_scelto['Materia']})
        * 📊 **Priorità Applicata:** _{cand_scelto['Priorità']}_
        """)
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Sì, Conferma Assegnazione", type="primary", use_container_width=True, key=f"dlg_btn_yes_{giorno_selezionato}_{ora_target}"):
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
                if gsheets_flag:
                    save_data_to_gsheets()
                st.success(f"Assegnato con successo **{cand_scelto['Docente']}** per la classe **{classe_target}** ({ora_target})!")
                st.rerun()
        with c2:
            if st.button("❌ Annulla", use_container_width=True, key=f"dlg_btn_no_{giorno_selezionato}_{ora_target}"):
                st.rerun()

tab_assenze, tab_sostituzioni, tab_registro = st.tabs([
    "📋 1. Inserimento Assenze del Giorno",
    "🎯 2. Quadro Ore Scoperte e Assegnazione Sostituti",
    "📊 3. Registro e Report Giornaliero"
])

# TAB 1: INSERIMENTO ASSENZE MULTI-DOCENTE
with tab_assenze:
    st.markdown(f"## 📋 Registrazione Assenze e Permessi per **{giorno_selezionato}**")
    st.write("Inserisci **tutti i docenti assenti della giornata** prima di assegnare le supplenze. L'algoritmo escluderà automaticamente questi docenti dalle disponibilità per evitare doppi incarichi.")

    if df_schedule.empty or 'Docente' not in df_schedule.columns:
        st.warning("⚠️ Carica prima un orario docenti valido dal pannello laterale per poter registrare le assenze.")
    else:
        lista_docenti_orario = sorted([str(d).strip() for d in df_schedule['Docente'].unique() if str(d).strip() and str(d).strip() != 'nan'])

        c_ins1, c_ins2, c_ins3 = st.columns([2.5, 2.0, 2.5])
        with c_ins1:
            docente_ass_sel = st.selectbox("Seleziona Docente Assente:", [""] + lista_docenti_orario, key=f"sel_doc_ass_{giorno_selezionato}")
        
        info_doc = df_schedule[df_schedule['Docente'] == docente_ass_sel].iloc[0] if docente_ass_sel and len(df_schedule[df_schedule['Docente'] == docente_ass_sel]) > 0 else {}
        mat_doc = str(info_doc.get('Materia', '')).strip()
        ind_doc = str(info_doc.get('Indirizzo', '')).strip()

        with c_ins2:
            tipo_ass_sel = st.radio("Tipologia Assenza:", ["🔴 Tutto il Giorno", "⏱️ Permesso Orario"], key=f"radio_tipo_ass_{giorno_selezionato}")

        ore_selezionate = []
        with c_ins3:
            if tipo_ass_sel == "⏱️ Permesso Orario":
                ore_selezionate = st.multiselect("Seleziona Ore di Assenza:", ORE, default=ORE[:2], key=f"multi_ore_ass_{giorno_selezionato}")
            else:
                st.info("L'assenza verrà registrata per l'intero orario di servizio della giornata.")
                ore_selezionate = ORE

        if docente_ass_sel:
            orario_items = []
            for slot in ORE:
                slot_short = slot.split(' ')[0]
                slot_key = f"{giorno_selezionato}_{slot}"
                val_slot = str(info_doc.get(slot_key, '')).strip()
                if not val_slot or val_slot.upper() in ['NAN', 'NONE', '']:
                    val_fmt = "Libero"
                elif val_slot.upper() in ['DISP', 'D', 'DISPOSIZIONE']:
                    val_fmt = "**DISP**"
                else:
                    val_fmt = f"**{val_slot}**"
                orario_items.append(f"{slot_short}: {val_fmt}")
            
            str_orario_doc = " | ".join(orario_items)
            st.info(f"📅 **Orario di servizio di {docente_ass_sel} per {giorno_selezionato}:** {str_orario_doc}")

        if st.button("➕ Registra Assenza Docente", type="primary", key=f"btn_add_ass_{giorno_selezionato}"):
            if not docente_ass_sel:
                st.error("Seleziona un docente dall'elenco.")
            elif tipo_ass_sel == "⏱️ Permesso Orario" and not ore_selezionate:
                st.error("Seleziona almeno un'ora di assenza.")
            else:
                gia_presente = any(item['Docente'] == docente_ass_sel for item in st.session_state.assenze_per_giorno[giorno_selezionato])
                if gia_presente:
                    st.warning(f"Il docente **{docente_ass_sel}** è già stato inserito tra gli assenti per {giorno_selezionato}.")
                else:
                    st.session_state.assenze_per_giorno[giorno_selezionato].append({
                        'Docente': docente_ass_sel,
                        'Materia': mat_doc,
                        'Indirizzo': ind_doc,
                        'Tipo': tipo_ass_sel,
                        'Ore': ore_selezionate
                    })
                    if gsheets_connected:
                        save_data_to_gsheets()
                    st.success(f"Assenza registrata per **{docente_ass_sel}**!")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"### 📌 Docenti Assenti Registrati per **{giorno_selezionato}**")

        curr_assenze = st.session_state.assenze_per_giorno.get(giorno_selezionato, [])
        if not curr_assenze:
            st.info("Nessun docente assente registrato per questo giorno.")
        else:
            th1, th2, th3, th4, th5, th6 = st.columns([2.5, 2.0, 1.5, 2.0, 2.0, 0.8])
            th1.markdown("**Docente assente**")
            th2.markdown("**Materia**")
            th3.markdown("**Indirizzo**")
            th4.markdown("**Tipologia assenza**")
            th5.markdown("**Ore coinvolte**")
            th6.markdown("**Azione**")
            st.markdown("---")

            for idx_a, item_a in enumerate(curr_assenze):
                ca1, ca2, ca3, ca4, ca5, ca6 = st.columns([2.5, 2.0, 1.5, 2.0, 2.0, 0.8])
                ca1.write(f"👤 **{item_a['Docente']}**")
                ca2.write(f"📚 {item_a.get('Materia', '-')}")
                ca3.write(f"🏫 {item_a.get('Indirizzo', '-')}")
                ca4.write(f"{item_a.get('Tipo', '-')}")

                d_nome_a = item_a['Docente']
                r_doc_a = df_schedule[df_schedule['Docente'] == d_nome_a]
                r_info_a = r_doc_a.iloc[0] if len(r_doc_a) > 0 else {}

                ore_range_a = item_a.get('Ore', []) if item_a.get('Tipo') != "🔴 Tutto il Giorno" else ORE
                
                ore_da_sostituire = []
                for slot in ore_range_a:
                    slot_key = f"{giorno_selezionato}_{slot}"
                    cls_val = str(r_info_a.get(slot_key, '')).strip()
                    if cls_val and cls_val.upper() not in ['NAN', '', 'NONE', 'DISP', 'D', 'DISPOSIZIONE']:
                        ore_da_sostituire.append(slot)

                if ore_da_sostituire:
                    short_hours = [o.split(' ')[0] for o in ore_da_sostituire]
                    ore_str = ", ".join(short_hours) + (" ora" if len(short_hours) == 1 else " ore")
                else:
                    ore_str = "Nessuna (solo DISP/libero)"

                ca5.write(f"⏱️ {ore_str}")
                if ca6.button("🗑️", key=f"btn_del_ass_{idx_a}_{giorno_selezionato}"):
                    doc_del = item_a['Docente']
                    st.session_state.assenze_per_giorno[giorno_selezionato].pop(idx_a)
                    st.session_state.registro = [
                        reg for reg in st.session_state.registro
                        if not (reg.get('Giorno') == giorno_selezionato and reg.get('Docente Assente') == doc_del)
                    ]
                    if gsheets_connected:
                        save_data_to_gsheets()
                    st.success(f"Rimossa assenza per **{doc_del}**.")
                    st.rerun()

# TAB 2: QUADRO ORE SCOPERTE E ASSEGNAZIONE SOSTITUTI
with tab_sostituzioni:
    st.markdown(f"## 🎯 Quadro Ore Scoperte e Ricerca Sostituti per **{giorno_selezionato}**")

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

            if cls_val and cls_val.upper() not in ['NAN', '', 'NONE']:
                if cls_val.upper() in ['DISP', 'D', 'DISPOSIZIONE']:
                    ore_disp_assenti_lista.append({
                        'Docente Assente': d_nome,
                        'Materia': d_mat,
                        'Ora': slot,
                        'Stato': 'DISP (Nessuna classe)'
                    })
                else:
                    if sostituto_assegnato:
                        if is_docente_assente_in_ora(sostituto_assegnato, giorno_selezionato, slot):
                            stato_sost = f"🚨 CONFLITTO ({sostituto_assegnato} ASSENTE!)"
                        else:
                            stato_sost = sostituto_assegnato
                    else:
                        stato_sost = "🔴 IN SOSPESO"

                    classi_scoperte_lista.append({
                        'Docente Assente': d_nome,
                        'Materia': d_mat,
                        'Ora': slot,
                        'Classe / Slot': cls_val,
                        'Sostituto Assegnato': stato_sost
                    })

    def sort_key_scoperte(item):
        sost = str(item.get('Sostituto Assegnato', ''))
        if sost == "🔴 IN SOSPESO":
            prio_status = 0
        elif "🚨 CONFLITTO" in sost:
            prio_status = 1
        else:
            prio_status = 2
        
        ora_val = item.get('Ora', '')
        ora_idx = ORE.index(ora_val) if ora_val in ORE else 99
        return (prio_status, ora_idx, str(item.get('Docente Assente', '')))

    classi_scoperte_lista.sort(key=sort_key_scoperte)

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
        else:
            st.info(f"📊 **Stato Copertura Classi ({giorno_selezionato}):** **{coperte_cnt}/{totale_scoperte}** ore coperte | 🔴 **{in_sospeso_cnt}** in sospeso" + (f" | 🚨 **{conflitti_cnt}** in conflitto" if conflitti_cnt > 0 else ""))

        st.markdown("#### 📌 Tabellone Riassuntivo delle Ore da Coprire")

        with st.container(height=300):
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

        st.markdown("---")
        st.subheader("🔍 Assegnazione Sostituto per un'Ora Scoperta")

        # CSS per lo sfondo azzurro chiaro della tendina e azzurro scuro/blu su hover e selezione
        st.markdown("""
        <style>
        /* Campo principale della selectbox: sfondo azzurro chiaro */
        div[data-baseweb="select"] > div {
            background-color: #e0f2fe !important;
            border: 1px solid #7dd3fc !important;
            border-radius: 6px !important;
        }
        div[data-baseweb="select"] * {
            color: #0369a1 !important;
            font-weight: 600 !important;
        }
        /* Lista del menu a comparsa (popover): sfondo azzurro chiaro */
        div[data-baseweb="popover"] ul, div[data-baseweb="menu"], div[role="listbox"] {
            background-color: #e0f2fe !important;
            border-radius: 6px !important;
        }
        /* Voci individuali nella lista: azzurro chiaro predefinito */
        div[data-baseweb="popover"] li, div[data-baseweb="menu"] li, div[role="option"] {
            background-color: #e0f2fe !important;
            color: #0369a1 !important;
            font-weight: 500 !important;
        }
        /* Quando si passa sopra col cursore (hover) o si seleziona: Azzurro Scuro / Blu con testo bianco */
        div[data-baseweb="popover"] li:hover, 
        div[data-baseweb="menu"] li:hover, 
        div[role="option"]:hover,
        div[data-baseweb="popover"] li[aria-selected="true"],
        div[data-baseweb="menu"] li[aria-selected="true"],
        div[role="option"][aria-selected="true"] {
            background-color: #1d4ed8 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        div[data-baseweb="popover"] li:hover *, 
        div[data-baseweb="menu"] li:hover *, 
        div[role="option"]:hover *,
        div[data-baseweb="popover"] li[aria-selected="true"] *,
        div[data-baseweb="menu"] li[aria-selected="true"] *,
        div[role="option"][aria-selected="true"] * {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)

        opzioni_scoperte = []
        for idx, row_s in enumerate(classi_scoperte_lista):
            stato_icon = "🟢" if ("🟢" in row_s['Sostituto Assegnato'] or (row_s['Sostituto Assegnato'] != "🔴 IN SOSPESO" and "🚨" not in row_s['Sostituto Assegnato'])) else ("🚨" if "🚨" in row_s['Sostituto Assegnato'] else "🔴")
            mat_str = f" | Materia: {row_s['Materia']}" if row_s.get('Materia') else ""
            opzioni_scoperte.append(f"{stato_icon} {row_s['Ora']} | Assente: {row_s['Docente Assente']} | Classe: {row_s['Classe / Slot']}{mat_str} | Sostituto: {row_s['Sostituto Assegnato']}")

        idx_scoperta_sel = st.selectbox(
            "Seleziona la lezione da coprire:",
            range(len(opzioni_scoperte)),
            format_func=lambda i: opzioni_scoperte[i],
            key=f"sel_ora_scoperta_{giorno_selezionato}"
        )

        target_slot = classi_scoperte_lista[idx_scoperta_sel]
        docente_assente_target = target_slot['Docente Assente']
        ora_target = target_slot['Ora']
        classe_target = target_slot['Classe / Slot']
        materia_target = target_slot['Materia']
        sostituto_corrente = target_slot['Sostituto Assegnato']

        esclusi_assenti = docenti_assenti_per_ora.get(ora_target, set())
        esclusi_sostituti = docenti_sostituti_occupati_per_ora.get(ora_target, set())
        tot_esclusi = esclusi_assenti.union(esclusi_sostituti)

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
            
            st.markdown("##### 👥 Candidati Disponibili (Clicca sulla riga per selezionare):")
            
            event_cands = st.dataframe(
                df_display,
                use_container_width=True,
                height=290,
                on_select="rerun",
                selection_mode="single-row",
                key=f"df_cands_{giorno_selezionato}_{ora_target}_{docente_assente_target}"
            )

            selected_rows = []
            if hasattr(event_cands, 'selection') and hasattr(event_cands.selection, 'rows'):
                selected_rows = event_cands.selection.rows
            elif isinstance(event_cands, dict) and 'selection' in event_cands and 'rows' in event_cands['selection']:
                selected_rows = event_cands['selection']['rows']

            if selected_rows and len(selected_rows) > 0:
                scelta_cand_idx = selected_rows[0]
            else:
                scelta_cand_idx = 0

            cand_scelto = all_cands[scelta_cand_idx]

            btn_label = "✅ Conferma / Riassegna Sostituto" if "🚨 CONFLITTO" in sostituto_corrente else "✅ Conferma Assegnazione Sostituto"
            if st.button(btn_label, type="primary"):
                if hasattr(st, 'dialog'):
                    confirm_sostituto_dialog(cand_scelto, giorno_selezionato, ora_target, docente_assente_target, classe_target, materia_target, gsheets_connected)
                else:
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

# TAB 3: REGISTRO E REPORT GIORNALIERO E SETTIMANALE
with tab_registro:
    st.markdown(f"## 📊 Registro delle Sostituzioni e Assenze per {giorno_selezionato}")

    reg_giorno = [r for r in st.session_state.get('registro', []) if r.get('Giorno') == giorno_selezionato]
    reg_giorno_sorted = sort_registro_by_day_and_teacher(reg_giorno)

    rows_display_giorno = []
    for r in reg_giorno_sorted:
        d_sost = r.get('Docente Sostituto', '')
        if is_docente_assente_in_ora(d_sost, giorno_selezionato, r.get('Ora', '')):
            stato = "🚨 CONFLITTO"
        elif d_sost and d_sost != '-':
            stato = "🟢 ASSEGNATO"
        else:
            stato = "🔴 IN SOSPESO"

        r_copy = dict(r)
        r_copy['Stato Sostituto'] = stato
        rows_display_giorno.append(r_copy)

    df_giorno = pd.DataFrame(rows_display_giorno)
    if not df_giorno.empty:
        cols_order = ['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']
        df_giorno = df_giorno.reindex(columns=[c for c in cols_order if c in df_giorno.columns])

    st.dataframe(df_giorno if not df_giorno.empty else pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']), use_container_width=True)

    today_str = datetime.date.today().strftime("%d/%m/%Y")
    pdf_bytes_giorno = create_circolare_pdf_bytes(giorno_selezionato, today_str, "", reg_giorno_sorted)

    col_btn_g1, col_btn_g2 = st.columns([1, 1])
    with col_btn_g1:
        if not df_giorno.empty:
            csv_giorno = df_giorno.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Report Sostituzioni di Oggi (CSV)",
                data=csv_giorno,
                file_name=f"Report_Sostituzioni_{giorno_selezionato}.csv",
                mime="text/csv"
            )
        else:
            st.button("📥 Scarica Report Sostituzioni di Oggi (CSV)", disabled=True)

    with col_btn_g2:
        st.download_button(
            label="📄 Scarica Circolare Sostituzioni (PDF)",
            data=pdf_bytes_giorno,
            file_name=f"Circolare_Sostituzioni_{giorno_selezionato}.pdf",
            mime="application/pdf"
        )

    st.markdown("---")
    st.markdown("### 📜 Storico Completo Sessione (Tutti i Giorni — Ordinato per Criticità, Stato e Docente)")

    reg_tot = sort_registro_by_day_and_teacher(st.session_state.get('registro', []))
    rows_display_tot = []
    for r in reg_tot:
        d_sost = r.get('Docente Sostituto', '')
        g_val = r.get('Giorno', '')
        o_val = r.get('Ora', '')
        if is_docente_assente_in_ora(d_sost, g_val, o_val):
            stato = "🚨 CONFLITTO"
        elif d_sost and d_sost != '-':
            stato = "🟢 ASSEGNATO"
        else:
            stato = "🔴 IN SOSPESO"

        r_copy = dict(r)
        r_copy['Stato Sostituto'] = stato
        rows_display_tot.append(r_copy)

    df_tot = pd.DataFrame(rows_display_tot)
    if not df_tot.empty:
        cols_order = ['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']
        df_tot = df_tot.reindex(columns=[c for c in cols_order if c in df_tot.columns])

    st.dataframe(df_tot if not df_tot.empty else pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']), use_container_width=True)

    pdf_bytes_tot = create_storico_pdf_bytes(today_str, reg_tot)

    col_btn_t1, col_btn_t2 = st.columns([1, 1])
    with col_btn_t1:
        if not df_tot.empty:
            csv_tot = df_tot.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Report Storico Completo Settimanale (CSV)",
                data=csv_tot,
                file_name="Report_Storico_Sostituzioni_Settimanale.csv",
                mime="text/csv"
            )
        else:
            st.button("📥 Scarica Report Storico Completo Settimanale (CSV)", disabled=True)

    with col_btn_t2:
        st.download_button(
            label="📄 Scarica Report Storico Completo (PDF)",
            data=pdf_bytes_tot,
            file_name="Report_Storico_Sostituzioni_Settimanale.pdf",
            mime="application/pdf"
        )
