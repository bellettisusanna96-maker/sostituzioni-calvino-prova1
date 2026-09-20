import streamlit as st
import pandas as pd
import io
import datetime
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from gspread_dataframe import get_as_dataframe, set_with_dataframe

### Attempt to import GSheetsConnection
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

### Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1a237e;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #3f51b5;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding-left: 16px;
        padding-right: 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a237e !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

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

    pdf.set_font('Helvetica', '', 10)
    intro_txt = f"Si comunicanole variazioni d'orario e le sostituzioni dei docenti assenti per la giornata di {giorno} ({data_str}). I docenti sostituti sono tenuti a firmare la presenza in classe sul Registro Elettronico."
    pdf.multi_cell(0, 5, clean_pdf_text(intro_txt))
    pdf.ln(6)

    if not rows:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, "Nessuna sostituzione o variazione d'orario programmata per la giornata odierna.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(230, 235, 245)
        pdf.set_draw_color(180, 190, 210)
        
        col_w = [25, 18, 42, 35, 42, 28]
        headers = ['Ora', 'Classe', 'Doc. Assente', 'Materia', 'Doc. Sostituto', 'Tipologia']
        
        for idx, h in enumerate(headers):
            pdf.cell(col_w[idx], 7, clean_pdf_text(h), border=1, align='C', fill=True)
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 8)
        for r in rows:
            ora_val = clean_pdf_text(str(r.get('Ora', '')).split(' ')[0])
            cls_val = clean_pdf_text(str(r.get('Classe', '')))
            ass_val = clean_pdf_text(str(r.get('Docente Assente', '')))
            mat_val = clean_pdf_text(str(r.get('Materia', '')))
            sost_val = clean_pdf_text(str(r.get('Docente Sostituto', '')))
            tipo_val = clean_pdf_text(str(r.get('Tipologia Sostituzione', '')))
            
            pdf.cell(col_w[0], 6, ora_val, border=1, align='C')
            pdf.cell(col_w[1], 6, cls_val, border=1, align='C')
            pdf.cell(col_w[2], 6, ass_val[:24], border=1, align='L')
            pdf.cell(col_w[3], 6, mat_val[:20], border=1, align='L')
            pdf.cell(col_w[4], 6, sost_val[:24], border=1, align='L')
            pdf.cell(col_w[5], 6, tipo_val[:16], border=1, align='C')
            pdf.ln()

    pdf.ln(8)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, clean_pdf_text("Il Dirigente Scolastico / Il Collaboratore del DS"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
    pdf.cell(0, 5, clean_pdf_text("I.I.S. \"Italo Calvino\" - Rozzano"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

    return bytes(pdf.output())

def create_storico_pdf_bytes(data_str, rows):
    pdf = CircolarePDF("Settimana", data_str)
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 35, 126)
    pdf.cell(0, 8, clean_pdf_text("REPORT STORICO SETTIMANALE SOSTITUZIONI"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, clean_pdf_text(f"Riepilogo completo di tutte le assenze e sostituzioni registrate nella sessione ({data_str})"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    if not rows:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 6, "Nessun dato registrato nello storico.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(230, 235, 245)
        pdf.set_draw_color(180, 190, 210)
        
        col_w = [22, 22, 38, 15, 30, 38, 25]
        headers = ['Giorno', 'Ora', 'Doc. Assente', 'Classe', 'Materia', 'Doc. Sostituto', 'Tipologia']
        
        for idx, h in enumerate(headers):
            pdf.cell(col_w[idx], 7, clean_pdf_text(h), border=1, align='C', fill=True)
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 8)
        for r in rows:
            g_val = clean_pdf_text(str(r.get('Giorno', '')))
            ora_val = clean_pdf_text(str(r.get('Ora', '')).split(' ')[0])
            ass_val = clean_pdf_text(str(r.get('Docente Assente', '')))
            cls_val = clean_pdf_text(str(r.get('Classe', '')))
            mat_val = clean_pdf_text(str(r.get('Materia', '')))
            sost_val = clean_pdf_text(str(r.get('Docente Sostituto', '')))
            tipo_val = clean_pdf_text(str(r.get('Tipologia Sostituzione', '')))
            
            pdf.cell(col_w[0], 6, g_val[:12], border=1, align='C')
            pdf.cell(col_w[1], 6, ora_val, border=1, align='C')
            pdf.cell(col_w[2], 6, ass_val[:22], border=1, align='L')
            pdf.cell(col_w[3], 6, cls_val, border=1, align='C')
            pdf.cell(col_w[4], 6, mat_val[:18], border=1, align='L')
            pdf.cell(col_w[5], 6, sost_val[:22], border=1, align='L')
            pdf.cell(col_w[6], 6, tipo_val[:14], border=1, align='C')
            pdf.ln()

    return bytes(pdf.output())

### Helper per accedere al client gspread in modo compatibile sia con le vecchie che con le nuove versioni di st-gsheets-connection
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
                if df is not None:
                    df = df.dropna(how='all').dropna(how='all', axis=1)
                    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
                return df if df is not None else pd.DataFrame()
    except Exception:
        pass

    try:
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

CLASSES_INFO = {
    '1A': ('ITE', 'Istituto Tecnico Economico'),
    '2A': ('ITE', 'Istituto Tecnico Economico'),
    '3A': ('ITE', 'Istituto Tecnico Economico'),
    '4A': ('ITE', 'Istituto Tecnico Economico'),
    '5A': ('ITE', 'Istituto Tecnico Economico'),
    '1B': ('ITE', 'Istituto Tecnico Economico'),
    '2B': ('ITE', 'Istituto Tecnico Economico'),
    '3B': ('ITE', 'Istituto Tecnico Economico'),
    '4B': ('ITE', 'Istituto Tecnico Economico'),
    '5B': ('ITE', 'Istituto Tecnico Economico'),
    '1C': ('LICEAL', 'Liceo Scientifico / Umane'),
    '2C': ('LICEAL', 'Liceo Scientifico / Umane'),
    '3C': ('LICEAL', 'Liceo Scientifico / Umane'),
    '4C': ('LICEAL', 'Liceo Scientifico / Umane'),
    '5C': ('LICEAL', 'Liceo Scientifico / Umane'),
    '1D': ('LICEAL', 'Liceo Scientifico / Umane'),
    '2D': ('LICEAL', 'Liceo Scientifico / Umane'),
    '3D': ('LICEAL', 'Liceo Scientifico / Umane'),
    '4D': ('LICEAL', 'Liceo Scientifico / Umane'),
    '5D': ('LICEAL', 'Liceo Scientifico / Umane'),
    '1E': ('PROF', 'Istituto Professionale'),
    '2E': ('PROF', 'Istituto Professionale'),
    '3E': ('PROF', 'Istituto Professionale'),
    '4E': ('PROF', 'Istituto Professionale'),
    '5E': ('PROF', 'Istituto Professionale')
}

default_teachers_data = [
    {
        'Docente': 'ROSSI Mario',
        'Materia': 'Matematica',
        'Indirizzo': 'ITE',
        'CdC': '1A, 2A, 3A',
        'Lunedì_1ª ora (08:00)': '1A',
        'Lunedì_2ª ora (08:55)': '2A',
        'Lunedì_3ª ora (10:00)': 'DISP',
        'Lunedì_4ª ora (10:55)': '3A'
    },
    {
        'Docente': 'VERDI Giuseppe',
        'Materia': 'Italiano',
        'Indirizzo': 'ITE',
        'CdC': '1A, 2A',
        'Lunedì_1ª ora (08:00)': '2A',
        'Lunedì_2ª ora (08:55)': 'DISP',
        'Lunedì_3ª ora (10:00)': '1A'
    },
    {
        'Docente': 'BIANCHI Anna',
        'Materia': 'Inglese',
        'Indirizzo': 'LICEAL',
        'CdC': '1C, 2C',
        'Lunedì_1ª ora (08:00)': 'DISP',
        'Lunedì_2ª ora (08:55)': '1C',
        'Lunedì_3ª ora (10:00)': '2C'
    }
]

def sort_registro_by_teacher_first(records):
    def sort_key(r):
        d_ass = str(r.get('Docente Assente', '')).strip().upper()
        g_val = r.get('Giorno', '')
        g_idx = GIORNI.index(g_val) if g_val in GIORNI else 99
        o_val = str(r.get('Ora', ''))
        o_idx = 99
        for i, slot in enumerate(ORE):
            if slot == o_val or slot.split(' ')[0] in o_val or o_val.split(' ')[0] in slot:
                o_idx = i
                break
        return (d_ass, g_idx, o_idx, str(r.get('Classe', '')))
    return sorted(records, key=sort_key)

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

### Session State Initialization
if 'assenze_per_giorno' not in st.session_state:
    st.session_state.assenze_per_giorno = {g: [] for g in GIORNI}
if 'registro' not in st.session_state:
    st.session_state.registro = []
if 'gsheets_loaded' not in st.session_state:
    st.session_state.gsheets_loaded = False
if 'df_schedule' not in st.session_state:
    st.session_state.df_schedule = pd.DataFrame()

### Google Sheets connection setup
conn = None
gsheets_connected = False
if HAS_GSHEETS:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        gsheets_connected = True
    except Exception:
        gsheets_connected = False

def save_schedule_to_gsheets(df_sch):
    if not gsheets_connected or conn is None:
        return False, "Google Fogli non connesso"
    try:
        ok, err = safe_gsheets_update(conn, "Orario", df_sch)
        return ok, err
    except Exception as e:
        return False, str(e)

def load_data_from_gsheets():
    if not gsheets_connected or conn is None:
        return False, "Connessione Google Fogli non disponibile"
    try:
        df_ora = safe_gsheets_read(conn, "Orario")
        if df_ora is not None and not df_ora.empty:
            df_norm = normalize_schedule_dataframe(df_ora)
            if not df_norm.empty and 'Docente' in df_norm.columns:
                st.session_state.df_schedule = df_norm

        df_ass = safe_gsheets_read(conn, "Assenze")
        if df_ass is not None and not df_ass.empty:
            assenze_dict = {g: [] for g in GIORNI}
            for _, row in df_ass.iterrows():
                g = str(row.get('Giorno', '')).strip()
                d_nome = str(row.get('Docente', '')).strip()
                d_mat = str(row.get('Materia', '')).strip()
                d_ind = str(row.get('Indirizzo', '')).strip()
                d_tipo = str(row.get('Tipo', '')).strip()
                ore_str = str(row.get('Ore', '')).strip()
                ore_list = [o.strip() for o in ore_str.split(',') if o.strip()] if ore_str else []
                if g in assenze_dict and d_nome and d_nome != 'nan':
                    assenze_dict[g].append({
                        'Docente': d_nome,
                        'Materia': d_mat,
                        'Indirizzo': d_ind,
                        'Tipo': d_tipo,
                        'Ore': ore_list
                    })
            st.session_state.assenze_per_giorno = assenze_dict

        df_reg = safe_gsheets_read(conn, "Registro")
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
                if g and ora and d_ass and d_sost and d_ass != 'nan' and d_sost != 'nan':
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
        return True, None
    except Exception as e:
        return False, str(e)

def save_data_to_gsheets():
    if not gsheets_connected or conn is None:
        return False
    try:
        rows_ass = []
        for g, list_a in st.session_state.assenze_per_giorno.items():
            for item in list_a:
                rows_ass.append({
                    'Giorno': g,
                    'Docente': item.get('Docente', ''),
                    'Materia': item.get('Materia', ''),
                    'Indirizzo': item.get('Indirizzo', ''),
                    'Tipo': item.get('Tipo', ''),
                    'Ore': ", ".join(item.get('Ore', [])) if isinstance(item.get('Ore'), list) else str(item.get('Ore', ''))
                })
        df_ass = pd.DataFrame(rows_ass)
        if df_ass.empty:
            df_ass = pd.DataFrame(columns=['Giorno', 'Docente', 'Materia', 'Indirizzo', 'Tipo', 'Ore'])
        ok1, err1 = safe_gsheets_update(conn, "Assenze", df_ass)
        if not ok1:
            st.session_state.gsheets_last_error = f"Errore scheda Assenze: {err1}"
            return False

        df_reg = pd.DataFrame(st.session_state.registro)
        if df_reg.empty:
            df_reg = pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Priorità Applicata'])
        ok2, err2 = safe_gsheets_update(conn, "Registro", df_reg)
        if not ok2:
            st.session_state.gsheets_last_error = f"Errore scheda Registro: {err2}"
            return False

        st.session_state.gsheets_last_error = None
        return True
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

def import_registro_from_csv(uploaded_csv_file, replace_existing=True):
    try:
        bytes_data = uploaded_csv_file.getvalue()
        try:
            df_imp = pd.read_csv(io.BytesIO(bytes_data))
        except Exception:
            df_imp = pd.read_csv(io.BytesIO(bytes_data), encoding='latin1')

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

def match_day_and_slot(c_str):
    c_upper = str(c_str).strip().upper()
    day_found = None
    days_map = {'LUN': 'Lunedì', 'MAR': 'Martedì', 'MER': 'Mercoledì', 'GIO': 'Giovedì', 'VEN': 'Venerdì'}
    for code, full in days_map.items():
        if code in c_upper or full.upper() in c_upper:
            day_found = full
            break
    if not day_found:
        for code, full in [('NED', 'Lunedì'), ('ART', 'Martedì'), ('ERC', 'Mercoledì'), ('IOV', 'Giovedì'), ('ENE', 'Venerdì')]:
            if code in c_upper:
                day_found = full
                break
    if not day_found:
        return None

    for slot_idx, slot in enumerate(ORE, start=1):
        num_str = str(slot_idx)
        patterns = [
            rf'{num_str}ª', rf'{num_str}A', rf'{num_str}°', rf'{num_str}\s*ORA', rf'ORA\s*{num_str}', rf'_{num_str}'
        ]
        if slot.upper() in c_upper or slot.split(' ')[0].upper() in c_upper:
            return f"{day_found}_{slot}"
        if any(re.search(p, c_upper) for p in patterns):
            return f"{day_found}_{slot}"
            
    return None

def normalize_schedule_dataframe(df):
    if df is None or df.empty:
        return pd.DataFrame()
    
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

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
            header = df.iloc[header_row_idx - 1]
            df = df.iloc[header_row_idx:].copy()
            df.columns = [str(c).strip() for c in header]

    col_mapping = {}

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
            mapped = match_day_and_slot(col)
            if mapped:
                col_mapping[col] = mapped

    df = df.rename(columns=col_mapping)

    if 'Docente' in df.columns:
        df = df[df['Docente'].notna() & (df['Docente'].astype(str).str.strip() != '') & (~df['Docente'].astype(str).str.upper().str.contains('DOCENTE', na=False))].copy()

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


def load_and_normalize_schedule(uploaded_file):
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()
    
    if file_name.endswith('.pdf'):
        tables_rows = []
        pdf_errors = []

        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted_tables = page.extract_tables()
                    if extracted_tables:
                        for table in extracted_tables:
                            for row in table:
                                if row and any(cell is not None and str(cell).strip() for cell in row):
                                    tables_rows.append([str(cell).strip() if cell is not None else '' for cell in row])
                    if not tables_rows:
                        text_p = page.extract_text()
                        if text_p:
                            for line_t in text_p.split('\n'):
                                parts = [p.strip() for p in re.split(r'\t+|\s{2,}', line_t) if p.strip()]
                                if parts:
                                    tables_rows.append(parts)
        except ImportError:
            pdf_errors.append("Libreria 'pdfplumber' non presente.")
        except Exception as e_pdfp:
            pdf_errors.append(f"Errore pdfplumber: {e_pdfp}")

        if not tables_rows:
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text_p = page.extract_text()
                    if text_p:
                        for line_t in text_p.split('\n'):
                            parts = [p.strip() for p in re.split(r'\t+|\s{2,}', line_t) if p.strip()]
                            if parts:
                                tables_rows.append(parts)
            except ImportError:
                pdf_errors.append("Libreria 'pypdf' non presente.")
            except Exception as e_pypdf:
                pdf_errors.append(f"Errore pypdf: {e_pypdf}")

        if not tables_rows:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text_p = page.extract_text()
                    if text_p:
                        for line_t in text_p.split('\n'):
                            parts = [p.strip() for p in re.split(r'\t+|\s{2,}', line_t) if p.strip()]
                            if parts:
                                tables_rows.append(parts)
            except ImportError:
                pdf_errors.append("Libreria 'PyPDF2' non presente.")
            except Exception as e_pypdf2:
                pdf_errors.append(f"Errore PyPDF2: {e_pypdf2}")

        if not tables_rows:
            details = ' '.join(pdf_errors)
            raise ValueError(f"Impossibile leggere il file PDF. Assicurati che il file contenga testo o tabelle e che sia installata una libreria PDF ('pypdf' o 'pdfplumber') nel file requirements.txt di Streamlit. {details}")

        df_raw = pd.DataFrame(tables_rows[1:], columns=tables_rows[0])
    elif file_name.endswith('.csv'):
        try:
            df_raw = pd.read_csv(io.BytesIO(file_bytes))
        except Exception:
            df_raw = pd.read_csv(io.BytesIO(file_bytes), encoding='latin1')
    else:
        df_raw = pd.read_excel(io.BytesIO(file_bytes))

    return normalize_schedule_dataframe(df_raw)

### SIDEBAR
st.sidebar.header("📁 1. Caricamento Orario")
uploaded_file = st.sidebar.file_uploader("Carica Quadro Orario (CSV/Excel/PDF)", type=['csv', 'xlsx', 'xls', 'pdf'])

if uploaded_file is not None:
    try:
        df_schedule = load_and_normalize_schedule(uploaded_file)
        st.session_state.df_schedule = df_schedule
        st.sidebar.success(f"✅ Nuovo Orario Caricato: {len(df_schedule)} docenti")
        if gsheets_connected:
            ok_s, err_s = save_schedule_to_gsheets(df_schedule)
            if ok_s:
                st.sidebar.success("☁️ Orario salvato permanentemente su Google Fogli!")
            else:
                st.sidebar.warning(f"⚠️ Impossibile salvare orario su Google Fogli: {err_s}")
    except Exception as e:
        st.sidebar.error(f"Errore caricamento: {e}")
        df_schedule = st.session_state.df_schedule if not st.session_state.df_schedule.empty else pd.DataFrame(default_teachers_data)
else:
    if 'df_schedule' in st.session_state and not st.session_state.df_schedule.empty:
        df_schedule = st.session_state.df_schedule
        st.sidebar.info(f"📋 Orario attivo: {len(df_schedule)} docenti")
    elif gsheets_connected:
        df_ora = safe_gsheets_read(conn, "Orario")
        if df_ora is not None and not df_ora.empty:
            df_norm = normalize_schedule_dataframe(df_ora)
            if not df_norm.empty and 'Docente' in df_norm.columns:
                st.session_state.df_schedule = df_norm
                df_schedule = df_norm
                st.sidebar.info(f"☁️ Orario caricato da Google Fogli: {len(df_schedule)} docenti")
            else:
                df_schedule = pd.DataFrame(default_teachers_data)
        else:
            df_schedule = pd.DataFrame(default_teachers_data)
    else:
        df_schedule = pd.DataFrame(default_teachers_data)

if gsheets_connected:
    if st.sidebar.button("🔄 Ricarica Orario da Google Fogli", key="btn_reload_schedule_gsheets"):
        df_ora = safe_gsheets_read(conn, "Orario")
        if df_ora is not None and not df_ora.empty:
            df_norm = normalize_schedule_dataframe(df_ora)
            if not df_norm.empty and 'Docente' in df_norm.columns:
                st.session_state.df_schedule = df_norm
                st.sidebar.success(f"✅ Ricaricati {len(df_norm)} docenti da Google Fogli!")
                st.rerun()
            else:
                st.sidebar.error("❌ Nessun docente valido trovato nella scheda 'Orario'.")
        else:
            st.sidebar.error("❌ Impossibile leggere la scheda 'Orario' da Google Fogli.")

st.sidebar.markdown("---")
st.sidebar.header("📊 2. Salvataggio Cloud")

if gsheets_connected:
    st.sidebar.success("🟩 **Google Fogli Collegato**")
    if getattr(st.session_state, 'gsheets_last_error', None):
        st.sidebar.error(f"⚠️ **Errore Salvataggio Cloud:** \n{st.session_state.gsheets_last_error}")
    if st.sidebar.button("🔄 Sincronizza / Ricarica da Cloud"):
        success, err_msg = load_data_from_gsheets()
        if success:
            st.sidebar.success("Dati ricaricati con successo!")
            st.rerun()
        else:
            st.sidebar.error(f"Errore durante la lettura da Google Fogli: {err_msg}")
else:
    st.sidebar.info("🟧 **Google Fogli Non Configurato**")
    st.sidebar.caption("I dati vengono salvati temporaneamente in memoria sessione. Collega Google Fogli per il salvataggio cloud permanente.")

with st.sidebar.expander("ℹ️ Guida Google Fogli"):
    st.markdown("""
    **Come attivare Google Fogli:**
    1. Crea un foglio su Google Fogli chiamato **Sostituzioni_Calvino** con tre schede: **Assenze**, **Registro** e **Orario**.
    2. Condividi il foglio con l'email del tuo Service Account Google (con permessi di modifica).
    3. Su Streamlit Cloud, vai su **Settings -> Secrets** e inserisci le credenziali [connections.gsheets].
    4. Assicurati che st-gsheets-connection sia presente nel file requirements.txt.
    """)

st.sidebar.markdown("---")
st.sidebar.header("📥 3. Importazione Backup")
uploaded_backup_csv = st.sidebar.file_uploader("Carica File CSV di Backup", type=['csv'], key="sidebar_csv_uploader")
if uploaded_backup_csv is not None:
    mode_imp = st.sidebar.radio("Modalità Importazione:", ["Sostituisci Registro", "Aggiungi al Registro"], key="radio_imp_mode")
    replace_flag = (mode_imp == "Sostituisci Registro")
    if st.sidebar.button("🔄 Ripristina Dati da CSV", type="primary"):
        if import_registro_from_csv(uploaded_backup_csv, replace_existing=replace_flag):
            st.rerun()

### MAIN INTERFACE
st.markdown("<div class='main-header'>🏫 I.I.S. ITALO CALVINO - ROZZANO</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Gestione Sostituzioni e Supplenze Docenti</div>", unsafe_allow_html=True)

c_day1, c_day2 = st.columns([1.5, 3.5])

with c_day1:
    giorno_selezionato = st.selectbox(
        "📅 **SELEZIONA IL GIORNO DI GESTIONE:**",
        GIORNI,
        index=0,
        key="main_day_selector",
        help="Scegli il giorno della settimana di cui vuoi gestire assenze e sostituzioni."
    )

tot_scop_g = 0
in_sosp_g = 0
confl_g = 0

tot_scop_settimana = 0
in_sosp_settimana = 0
confl_settimana = 0
giorni_con_scoperti = []

for g_check in GIORNI:
    tot_g_c = 0
    in_sosp_g_c = 0
    confl_g_c = 0
    if 'assenze_per_giorno' in st.session_state and g_check in st.session_state.assenze_per_giorno:
        for item_ass in st.session_state.assenze_per_giorno[g_check]:
            d_n = item_ass['Docente']
            r_d = df_schedule[df_schedule['Docente'] == d_n]
            r_i = r_d.iloc[0] if len(r_d) > 0 else {}
            ore_eff = item_ass['Ore'] if item_ass.get('Tipo') != "🔴 Tutto il Giorno" else ORE

            for slot_o in ore_eff:
                s_k = f"{g_check}_{slot_o}"
                c_v = str(r_i.get(s_k, '')).strip()
                if c_v and c_v.upper() not in ['NAN', '', 'DISP', 'D', 'DISPOSIZIONE']:
                    tot_g_c += 1
                    sost_ass = None
                    for reg in st.session_state.get('registro', []):
                        if reg.get('Giorno') == g_check and reg.get('Ora') == slot_o and reg.get('Docente Assente') == d_n:
                            sost_ass = reg.get('Docente Sostituto')
                            break
                    if not sost_ass:
                        in_sosp_g_c += 1
                    elif is_docente_assente_in_ora(sost_ass, g_check, slot_o):
                        confl_g_c += 1

    tot_scop_settimana += tot_g_c
    in_sosp_settimana += in_sosp_g_c
    confl_settimana += confl_g_c
    if (in_sosp_g_c + confl_g_c) > 0:
        giorni_con_scoperti.append(g_check)

    if g_check == giorno_selezionato:
        tot_scop_g = tot_g_c
        in_sosp_g = in_sosp_g_c
        confl_g = confl_g_c

with c_day2:
    if tot_scop_settimana > 0 and in_sosp_settimana == 0 and confl_settimana == 0:
        st.success("🌟 **QUADRO SETTIMANALE:** 🎉 TUTTA LA SETTIMANA È COPERTA! Tutte le classi dei 5 giorni hanno un sostituto assegnato.")
    elif in_sosp_settimana > 0 or confl_settimana > 0:
        altri_giorni = [g for g in giorni_con_scoperti if g != giorno_selezionato]
        if altri_giorni:
            st.warning(f"⚠️ **ALTRI GIORNI DA COPRIRE:** Ci sono ancora classi scoperte in: **{', '.join(altri_giorni)}**")
        else:
            st.info("ℹ️ **QUADRO SETTIMANALE:** Negli altri giorni della settimana tutte le classi risultano coperte.")
    else:
        st.caption("ℹ️ **Quadro Settimanale:** Nessuna classe da sostituire registrata finora per gli altri giorni della settimana.")

st.markdown("---")
st.session_state.giorno_corrente = giorno_selezionato
if giorno_selezionato not in st.session_state.assenze_per_giorno:
    st.session_state.assenze_per_giorno[giorno_selezionato] = []

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
        f"🚨 **ALLERTA CRITICA ({len(conflitti_attivi)} CONFLITTO/I RILEVATO/I):** Ci sono docenti assegnati in supplenza che risultano **ASSENTI**!\n\n" +
        "\n".join(dettagli_conf) +
        "\n\n👉 *Vai nel* ***TAB 2 (Quadro Ore Scoperte)*** *per riassegnare un nuovo sostituto a questa/e classe/i!*"
    )

if hasattr(st, 'dialog'):
    @st.dialog("⚠️ Conferma Assegnazione Sostituto")
    def confirm_sostituto_dialog(cand_scelto, giorno_selezionato, ora_target, docente_assente_target, classe_target, materia_target, gsheets_flag):
        st.markdown(f"### Confermi l'assegnazione di **{cand_scelto['Docente']}**?")
        st.markdown(f"""
        * 📅 **Giorno:** {giorno_selezionato}
        * ⏱️ **Ora:** {ora_target}
        * 🏫 **Classe:** {classe_target}
        * 📚 **Materia:** {materia_target}
        * 👤 **Docente Assente:** {docente_assente_target}
        * 🟢 **Docente Sostituto:** **{cand_scelto['Docente']}** ({cand_scelto['Materia']})
        * 📊 **Priorità Applicata:** *{cand_scelto['Priorità']}*
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
                st.success(f"Assegnato con successo **{cand_scelto['Docente']}**!")
                st.rerun()
        with c2:
            if st.button("❌ Annulla", use_container_width=True, key=f"dlg_btn_no_{giorno_selezionato}_{ora_target}"):
                st.rerun()

tab_assenze, tab_sostituzioni, tab_registro = st.tabs([
    "📋 1. Inserimento Assenze del Giorno",
    "🎯 2. Quadro Ore Scoperte e Assegnazione Sostituti",
    "📊 3. Registro e Report Giornaliero"
])

### TAB 1: INSERIMENTO ASSENZE MULTI-DOCENTE
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

        st.markdown("---")
        st.markdown("### 🗓️ Registrazione Assenze e Permessi della Settimana")

        all_weekly_absences = []
        for g_w in GIORNI:
            for idx_w, item_w in enumerate(st.session_state.assenze_per_giorno.get(g_w, [])):
                all_weekly_absences.append((g_w, idx_w, item_w))

        if not all_weekly_absences:
            st.info("Nessuna assenza registrata per l'intera settimana.")
        else:
            th_w1, th_w2, th_w3, th_w4, th_w5, th_w6, th_w7 = st.columns([1.5, 2.5, 2.0, 1.5, 2.0, 2.0, 0.8])
            th_w1.markdown("**Giorno**")
            th_w2.markdown("**Docente assente**")
            th_w3.markdown("**Materia**")
            th_w4.markdown("**Indirizzo**")
            th_w5.markdown("**Tipologia assenza**")
            th_w6.markdown("**Ore coinvolte**")
            th_w7.markdown("**Azione**")
            st.markdown("---")

            for g_w, idx_w, item_w in all_weekly_absences:
                cw1, cw2, cw3, cw4, cw5, cw6, cw7 = st.columns([1.5, 2.5, 2.0, 1.5, 2.0, 2.0, 0.8])
                cw1.write(f"📅 **{g_w}**")
                cw2.write(f"👤 **{item_w['Docente']}**")
                cw3.write(f"📚 {item_w.get('Materia', '-')}")
                cw4.write(f"🏫 {item_w.get('Indirizzo', '-')}")
                cw5.write(f"{item_w.get('Tipo', '-')}")

                d_nome_w = item_w['Docente']
                r_doc_w = df_schedule[df_schedule['Docente'] == d_nome_w]
                r_info_w = r_doc_w.iloc[0] if len(r_doc_w) > 0 else {}

                ore_range_w = item_w.get('Ore', []) if item_w.get('Tipo') != "🔴 Tutto il Giorno" else ORE

                ore_da_sostituire_w = []
                for slot in ore_range_w:
                    slot_key = f"{g_w}_{slot}"
                    cls_val = str(r_info_w.get(slot_key, '')).strip()
                    if cls_val and cls_val.upper() not in ['NAN', '', 'NONE', 'DISP', 'D', 'DISPOSIZIONE']:
                        ore_da_sostituire_w.append(slot)

                if ore_da_sostituire_w:
                    short_hours_w = [o.split(' ')[0] for o in ore_da_sostituire_w]
                    ore_str_w = ", ".join(short_hours_w) + (" ora" if len(short_hours_w) == 1 else " ore")
                else:
                    ore_str_w = "Nessuna (solo DISP/libero)"

                cw6.write(f"⏱️ {ore_str_w}")
                if cw7.button("🗑️", key=f"btn_del_ass_weekly_{g_w}_{idx_w}_{item_w['Docente']}"):
                    doc_del_w = item_w['Docente']
                    st.session_state.assenze_per_giorno[g_w].pop(idx_w)
                    st.session_state.registro = [
                        reg for reg in st.session_state.registro
                        if not (reg.get('Giorno') == g_w and reg.get('Docente Assente') == doc_del_w)
                    ]
                    if gsheets_connected:
                        save_data_to_gsheets()
                    st.success(f"Rimossa assenza per **{doc_del_w}** ({g_w}).")
                    st.rerun()

### TAB 2: QUADRO ORE SCOPERTE E ASSEGNAZIONE SOSTITUTI
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
        indirizzo_codice, indirizzo_nome = CLASSES_INFO.get(classe_target if classe_target != 'DISP' else '1A', ('ITE', 'Istituto Tecnico Economico'))

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

### TAB 3: REGISTRO E REPORT GIORNALIERO E SETTIMANALE
with tab_registro:
    st.markdown(f"## 📊 Registro delle Sostituzioni e Assenze per {giorno_selezionato}")

    # Filtraggio sostituzioni del giorno selezionato
    reg_giorno = [r for r in st.session_state.get('registro', []) if r.get('Giorno') == giorno_selezionato]
    reg_giorno_sorted = sort_registro_by_day_and_teacher(reg_giorno)

    # Aggiungiamo lo stato visuale per ciascuna riga
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

    st.dataframe(
        df_giorno if not df_giorno.empty else pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']),
        use_container_width=True,
        hide_index=True
    )

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

    st.markdown("#### 🔍 Filtri di Ricerca Rapida nello Storico")

    reg_tot_raw = st.session_state.get('registro', [])

    # Opzioni uniche per i filtri
    classi_uniche = sorted(list(set(str(r.get('Classe', '')).strip() for r in reg_tot_raw if str(r.get('Classe', '')).strip())))
    docenti_assenti_unici = sorted(list(set(str(r.get('Docente Assente', '')).strip() for r in reg_tot_raw if str(r.get('Docente Assente', '')).strip())))
    docenti_sostituti_unici = sorted(list(set(str(r.get('Docente Sostituto', '')).strip() for r in reg_tot_raw if str(r.get('Docente Sostituto', '')).strip() and str(r.get('Docente Sostituto', '')).strip() != '-')))
    tipologie_uniche = sorted(list(set(str(r.get('Tipologia Sostituzione', '')).strip() for r in reg_tot_raw if str(r.get('Tipologia Sostituzione', '')).strip())))

    fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1])
    with fc1:
        sel_classe = st.selectbox("🏫 Filtra per Classe:", ["Tutte le Classi"] + classi_uniche, key="filter_classe")
    with fc2:
        sel_doc_assente = st.selectbox("👤 Filtra per Docente Assente:", ["Tutti i Docenti Assenti"] + docenti_assenti_unici, key="filter_doc_assente")
    with fc3:
        sel_doc_sostituto = st.selectbox("👤 Filtra per Docente Sostituto:", ["Tutti i Docenti Sostituti"] + docenti_sostituti_unici, key="filter_doc_sostituto")
    with fc4:
        sel_tipologia = st.selectbox("📜 Filtra per Tipologia:", ["Tutte le Tipologie"] + (tipologie_uniche if tipologie_uniche else ["DISP", "EXTRA"]), key="filter_tipologia")

    has_filter = (sel_classe != "Tutte le Classi") or (sel_doc_assente != "Tutti i Docenti Assenti") or (sel_doc_sostituto != "Tutti i Docenti Sostituti") or (sel_tipologia != "Tutte le Tipologie")

    if not has_filter:
        reg_tot_sorted = sort_registro_by_teacher_first(reg_tot_raw)
    else:
        reg_tot_sorted = sort_registro_by_day_and_teacher(reg_tot_raw)

    rows_display_tot = []
    for r in reg_tot_sorted:
        g_val = r.get('Giorno', '')
        o_val = r.get('Ora', '')
        d_ass = str(r.get('Docente Assente', '')).strip()
        c_val = str(r.get('Classe', '')).strip()
        d_sost = str(r.get('Docente Sostituto', '')).strip()
        t_val = str(r.get('Tipologia Sostituzione', '')).strip()

        if sel_classe != "Tutte le Classi" and c_val != sel_classe:
            continue
        if sel_doc_assente != "Tutti i Docenti Assenti" and d_ass != sel_doc_assente:
            continue
        if sel_doc_sostituto != "Tutti i Docenti Sostituti" and d_sost != sel_doc_sostituto:
            continue
        if sel_tipologia != "Tutte le Tipologie" and sel_tipologia.upper() not in t_val.upper():
            continue

        if is_docente_assente_in_ora(d_sost, g_val, o_val):
            stato = "🚨 CONFLITTO"
        elif d_sost and d_sost != '-':
            stato = "🟢 ASSEGNATO"
        else:
            stato = "🔴 IN SOSPESO"

        r_copy = dict(r)
        r_copy['Stato Sostituto'] = stato
        rows_display_tot.append(r_copy)

    if sel_doc_sostituto != "Tutti i Docenti Sostituti":
        cnt_disp = sum(1 for r in rows_display_tot if 'DISP' in str(r.get('Tipologia Sostituzione', '')).upper())
        cnt_extra = sum(1 for r in rows_display_tot if 'EXTRA' in str(r.get('Tipologia Sostituzione', '')).upper())
        cnt_tot = len(rows_display_tot)
        st.info(f"📊 **Riepilogo Supplenze per {sel_doc_sostituto}:** **{cnt_tot}** supplenze coperte in totale (🟢 **{cnt_disp}** in ora DISP | 🔵 **{cnt_extra}** in ora EXTRA / Straordinario)")

    if sel_doc_assente != "Tutti i Docenti Assenti":
        cnt_ass_tot = sum(1 for r in rows_display_tot if r.get('Docente Assente') == sel_doc_assente)
        st.info(f"📊 **Riepilogo Assenze per {sel_doc_assente}:** **{cnt_ass_tot}** ore di assenza registrate nello storico.")

    df_tot = pd.DataFrame(rows_display_tot)
    if not df_tot.empty:
        cols_order = ['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']
        df_tot = df_tot.reindex(columns=[c for c in cols_order if c in df_tot.columns])

    st.dataframe(
        df_tot if not df_tot.empty else pd.DataFrame(columns=['Giorno', 'Ora', 'Docente Assente', 'Classe', 'Materia', 'Docente Sostituto', 'Tipologia Sostituzione', 'Stato Sostituto', 'Priorità Applicata']),
        use_container_width=True,
        hide_index=True
    )

    pdf_bytes_tot = create_storico_pdf_bytes(today_str, rows_display_tot)

    col_btn_t1, col_btn_t2, col_btn_t3 = st.columns([1.2, 1.2, 1.0])
    with col_btn_t1:
        if not df_tot.empty:
            csv_tot = df_tot.to_csv(index=False).encode('utf-8')
            label_csv = "📥 Scarica Report Storico Filtrato (CSV)" if has_filter else "📥 Scarica Report Storico Completo Settimanale (CSV)"
            st.download_button(
                label=label_csv,
                data=csv_tot,
                file_name="Report_Storico_Sostituzioni.csv",
                mime="text/csv"
            )
        else:
            st.button("📥 Scarica Report Storico (CSV)", disabled=True)

    with col_btn_t2:
        label_pdf = "📄 Scarica Report Storico Filtrato (PDF)" if has_filter else "📄 Scarica Report Storico Completo (PDF)"
        st.download_button(
            label=label_pdf,
            data=pdf_bytes_tot,
            file_name="Report_Storico_Sostituzioni.pdf",
            mime="application/pdf"
        )

    with col_btn_t3:
        if st.button("🗑️ Cancella Tutto il Registro"):
            st.session_state.registro = []
            if gsheets_connected:
                save_data_to_gsheets()
            st.success("Registro azzerato con successo!")
            st.rerun()
