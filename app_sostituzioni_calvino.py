import streamlit as st
import pandas as pd
import json

# ==============================================================================
# I.I.S. ITALO CALVINO - ROZZANO (A.S. 2026/2027)
# SISTEMA AUTOMATIZZATO GESTIONE SOSTITUZIONI DOCENTI
# ==============================================================================

st.set_page_config(
    page_title="Gestione Sostituzioni - I.I.S. Calvino",
    page_icon="🏫",
    layout="wide"
)

# Title & Subtitle
st.title("🏫 I.I.S. 'Italo Calvino' - Rozzano")
st.subheader("Sistema Automatico Gestione Sostituzioni e Supplenze (A.S. 2026/2027)")

st.markdown("""
Questo sistema automatizza l'individuazione dei sostituti per i docenti assenti applicando rigorosamente la gerarchia di priorità stabilita dall'istituto.
""")

# Sample Data Setup based on I.I.S. Calvino Sources
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

# Example Teachers Database
TEACHERS_DB = {
    'ACCIAVATTI Luciana': {'materia': 'Filosofia e Storia (A019)', 'indirizzo_princ': 'LS', 'cdc': ['3B', '4B', '5B', '4H']},
    'BONO Lamberto': {'materia': 'Economia Aziendale (A045)', 'indirizzo_princ': 'ITE', 'cdc': ['1a', '3a', '5a']},
    'CACCIUOTTOLO Adalgisa': {'materia': 'Filosofia e Storia (A019)', 'indirizzo_princ': 'LS', 'cdc': ['3A', '3F', '4F', '5F']},
    'FEDELI Angelo': {'materia': 'Economia Aziendale (A045)', 'indirizzo_princ': 'ITE', 'cdc': ['2b', '2c', '3d']},
    'GIANNUZZO Nadia': {'materia': 'Economia Aziendale (A045)', 'indirizzo_princ': 'ITE', 'cdc': ['3b', '4b', '5b']},
    'BARRACO Maria Laura': {'materia': 'Italiano e Latino (A011)', 'indirizzo_princ': 'LS', 'cdc': ['1B', '2F', '5B']},
    'PELIZZONI Luisa': {'materia': 'Italiano e Latino (A011)', 'indirizzo_princ': 'LS', 'cdc': ['2A', '4A']},
    'SALINA Paola': {'materia': 'Matematica e Fisica (A027)', 'indirizzo_princ': 'LS', 'cdc': ['3B', '4B', '5B']},
    'VILLELLA Vincenzo': {'materia': 'Matematica e Fisica (A027)', 'indirizzo_princ': 'LS', 'cdc': ['1A', '3A', '1B', '5B', '5F']},
    'DE CASTRO Calogero': {'materia': 'Scienze Motorie (A048)', 'indirizzo_princ': 'LS', 'cdc': ['1A', '2A', '3A', '4A', '5A', '1B', '3B', '4B', '5B']},
    'MARAFIOTI Giulia Francesca': {'materia': 'Religione (IRC)', 'indirizzo_princ': 'LS', 'cdc': ['1A', '2A', '3A', '4A', '5A', '1B', '2B', '3B', '4B', '5B', '1D', '2D', '3D', '4D', '5D', '2F', '3F', '4F']},
    'SERIOLI Romana Carolina': {'materia': 'Disegno e Arte (A017)', 'indirizzo_princ': 'LS', 'cdc': ['1A', '2A', '3A', '4A', '5A', '1B', '3B', '4B', '5B']},
    'PRIMO Antonella': {'materia': 'Scienze Naturali (A050)', 'indirizzo_princ': 'LS', 'cdc': ['1B', '2B', '3B', '4B', '5B', '1E']},
    'FELICETTI Monica': {'materia': 'Inglese (AB24)', 'indirizzo_princ': 'LS', 'cdc': ['1B', '2B', '3B', '4B', '5B', '5D']},
    'SUFFANTI': {'materia': 'Filosofia e Storia (A019)', 'indirizzo_princ': 'LSU', 'cdc': ['3H']},
    'VERDELLI Federica': {'materia': 'Scienze Umane (A018)', 'indirizzo_princ': 'LSU', 'cdc': ['5F', '1H', '2H', '3H']},
}

# Example DISP Schedule (Giorno -> Ora -> Lista Docenti in DISP)
DISP_SCHEDULE = {
    'Lunedì': {
        '1ª ora': ['SUFFANTI'],
        '2ª ora': ['BONO Lamberto', 'FEDELI Angelo', 'SUFFANTI'],
        '4ª ora': ['ACCIAVATTI Luciana', 'SUFFANTI'],
        '5ª ora': ['FEDELI Angelo', 'GIANNUZZO Nadia'],
        '6ª ora': ['BONO Lamberto', 'FEDELI Angelo', 'SUFFANTI'],
        '7ª ora': ['DI NUNNO Gaetana', 'FEDELI Angelo', 'SUFFANTI']
    },
    'Martedì': {
        '4ª ora': ['FEDELI Angelo'],
        '5ª ora': ['FEDELI Angelo'],
        '6ª ora': ['FEDELI Angelo'],
        '7ª ora': ['FEDELI Angelo', 'VERDELLI Federica']
    },
    'Mercoledì': {
        '6ª ora': ['FEDELI Angelo'],
        '7ª ora': ['FEDELI Angelo']
    },
    'Giovedì': {
        '5ª ora': ['GIANNUZZO Nadia'],
        '6ª ora': ['CACCIUOTTOLO Adalgisa', 'FEDELI Angelo'],
        '7ª ora': ['FEDELI Angelo']
    },
    'Venerdì': {
        '6ª ora': ['FEDELI Angelo'],
        '7ª ora': ['FEDELI Angelo']
    }
}

# Session State for Substitutions Register
if 'registro_sostituzioni' not in st.session_state:
    st.session_state.registro_sostituzioni = []

# Sidebar - Inputs
st.sidebar.header("📋 Inserisci Dati Assenza")
docente_assente = st.sidebar.selectbox("Docente Assente", list(TEACHERS_DB.keys()))
giorno = st.sidebar.selectbox("Giorno della Settimana", ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì'])
ora = st.sidebar.selectbox("Ora di Lezione", ['1ª ora', '2ª ora', '3ª ora', '4ª ora', '5ª ora', '6ª ora', '7ª ora'])
classe_lezione = st.sidebar.selectbox("Classe da Coprire", list(CLASSES_INFO.keys()), index=9) # Default 5B

materia_assente = TEACHERS_DB[docente_assente]['materia']
indirizzo_classe = CLASSES_INFO[classe_lezione]

st.sidebar.markdown("---")
st.sidebar.info(f"**Classe**: {classe_lezione} ({indirizzo_classe})\n\n**Materia**: {materia_assente}")

# Search Button
if st.sidebar.button("🔍 Cerca Sostituto In Automatico", type="primary"):
    st.subheader(f"📌 Risultati Ricerca Sostituto per {docente_assente}")
    st.write(f"**Giorno/Ora**: {giorno} - {ora} | **Classe**: {classe_lezione} ({indirizzo_classe}) | **Materia da coprire**: {materia_assente}")
    
    # Get available DISP teachers for day/hour
    docenti_in_disp = DISP_SCHEDULE.get(giorno, {}).get(ora, [])
    
    # Priority lists
    p1_cdc = []
    p2a_ind_materia = []
    p2b_ind_altra = []
    p3a_ext_materia = []
    p3b_ext_altra = []
    
    for doc in docenti_in_disp:
        if doc == docente_assente:
            continue
        
        info = TEACHERS_DB.get(doc, {'materia': 'Generica', 'indirizzo_princ': 'Generico', 'cdc': []})
        doc_materia = info['materia']
        doc_indirizzo = info['indirizzo_princ']
        doc_cdc = info['cdc']
        
        # P1: Same CDC
        if classe_lezione in doc_cdc:
            p1_cdc.append((doc, doc_materia, "Docente del Consiglio di Classe"))
        # P2: Same Address
        elif doc_indirizzo == indirizzo_classe:
            if doc_materia == materia_assente:
                p2a_ind_materia.append((doc, doc_materia, "Stesso Indirizzo - Stessa Materia"))
            else:
                p2b_ind_altra.append((doc, doc_materia, "Stesso Indirizzo - Altra Materia"))
        # P3: Other Address
        else:
            if doc_materia == materia_assente:
                p3a_ext_materia.append((doc, doc_materia, "Altro Indirizzo - Stessa Materia"))
            else:
                p3b_ext_altra.append((doc, doc_materia, "Altro Indirizzo - Altra Materia"))

    # Display Results according to Priority Cascade
    found = False
    
    if p1_cdc:
        found = True
        st.success("🟢 **PRIORITÀ 1 TROVATA: Docente a Disposizione nello Stesso Consiglio di Classe**")
        for doc, mat, note in p1_cdc:
            col1, col2 = st.columns([3, 1])
            col1.write(f"👤 **{doc}** — {mat} ({note})")
            if col2.button(f"Assegna (DISP)", key=f"assign_{doc}_p1"):
                st.session_state.registro_sostituzioni.append({
                    'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                    'Giorno': giorno, 'Ora': ora, 'Tipo': 'DISP (Orario d\'obbligo)', 'Priorita': 'P1 - Consiglio di Classe'
                })
                st.balloons()
                st.success(f"Sostituzione assegnata a {doc}!")

    elif p2a_ind_materia or p2b_ind_altra:
        found = True
        st.info("🔵 **PRIORITÀ 2 TROVATA: Docente a Disposizione nello Stesso Indirizzo**")
        if p2a_ind_materia:
            st.markdown("##### 2a. Stessa Materia dell'Assente")
            for doc, mat, note in p2a_ind_materia:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{doc}** — {mat}")
                if col2.button(f"Assegna (DISP)", key=f"assign_{doc}_p2a"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'DISP (Orario d\'obbligo)', 'Priorita': 'P2a - Stesso Indirizzo/Materia'
                    })
                    st.success(f"Sostituzione assegnata a {doc}!")
        if p2b_ind_altra:
            st.markdown("##### 2b. Altra Materia")
            for doc, mat, note in p2b_ind_altra:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{doc}** — {mat}")
                if col2.button(f"Assegna (DISP)", key=f"assign_{doc}_p2b"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'DISP (Orario d\'obbligo)', 'Priorita': 'P2b - Stesso Indirizzo/Altra Materia'
                    })
                    st.success(f"Sostituzione assegnata a {doc}!")

    elif p3a_ext_materia or p3b_ext_altra:
        found = True
        st.warning("🟡 **PRIORITÀ 3 TROVATA: Docente a Disposizione in Altro Indirizzo**")
        if p3a_ext_materia:
            st.markdown("##### 3a. Stessa Materia dell'Assente")
            for doc, mat, note in p3a_ext_materia:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{doc}** — {mat}")
                if col2.button(f"Assegna (DISP)", key=f"assign_{doc}_p3a"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'DISP (Orario d\'obbligo)', 'Priorita': 'P3a - Altro Indirizzo/Stessa Materia'
                    })
                    st.success(f"Sostituzione assegnata a {doc}!")
        if p3b_ext_altra:
            st.markdown("##### 3b. Altra Materia")
            for doc, mat, note in p3b_ext_altra:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 **{doc}** — {mat}")
                if col2.button(f"Assegna (DISP)", key=f"assign_{doc}_p3b"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'DISP (Orario d\'obbligo)', 'Priorita': 'P3b - Altro Indirizzo/Altra Materia'
                    })
                    st.success(f"Sostituzione assegnata a {doc}!")

    if not found:
        st.error("🔴 **FALLBACK (PRIORITÀ 4): Nessun docente con orario a disposizione (DISP) trovato in quest'ora.**")
        st.markdown("### 📞 Elenco Docenti Liberi da Contattare per Supplenza Straordinaria")
        st.write("Di seguito i docenti disponibili privi di lezione in quest'ora, suddivisi per tipologia di orario:")
        
        tab1, tab2, tab3 = st.tabs(["🕳️ Ora Buca in Orario", "⏰ Entrata Anticipata (+1h)", "⌛ Uscita Posticipata (+1h)"])
        
        with tab1:
            st.write("Docenti che hanno lezione l'ora precedente e l'ora successiva:")
            buca_docenti = [('SALINA Paola', 'Matematica e Fisica (LS)'), ('BARRACO Maria Laura', 'Italiano e Latino (LS)')]
            for doc, mat in buca_docenti:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{doc}** — {mat}")
                if c2.button(f"Assegna Extra", key=f"assign_{doc}_buca"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'EXTRA (Straordinario/Ora Buca)', 'Priorita': 'P4 - Ora Buca'
                    })
                    st.success(f"Sostituzione straordinaria assegnata a {doc}!")
        
        with tab2:
            st.write("Docenti che iniziano il servizio l'ora successiva:")
            anticipo_docenti = [('VILLELLA Vincenzo', 'Matematica e Fisica (LS)'), ('DE CASTRO Calogero', 'Scienze Motorie (LS)')]
            for doc, mat in anticipo_docenti:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{doc}** — {mat}")
                if c2.button(f"Assegna Extra", key=f"assign_{doc}_ant"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'EXTRA (Straordinario/Anticipo)', 'Priorita': 'P4 - Entrata Anticipata'
                    })
                    st.success(f"Sostituzione straordinaria assegnata a {doc}!")
                    
        with tab3:
            st.write("Docenti che terminano il servizio l'ora precedente:")
            posticipo_docenti = [('FELICETTI Monica', 'Inglese (LS)'), ('SERIOLI Romana Carolina', 'Arte (LS)')]
            for doc, mat in posticipo_docenti:
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{doc}** — {mat}")
                if c2.button(f"Assegna Extra", key=f"assign_{doc}_post"):
                    st.session_state.registro_sostituzioni.append({
                        'Docente': doc, 'Assente': docente_assente, 'Classe': classe_lezione,
                        'Giorno': giorno, 'Ora': ora, 'Tipo': 'EXTRA (Straordinario/Posticipo)', 'Priorita': 'P4 - Uscita Posticipata'
                    })
                    st.success(f"Sostituzione straordinaria assegnata a {doc}!")

# Annual Register View
st.markdown("---")
st.header("📊 Registro Annuale Sostituzioni Svolte dai Docenti")

if st.session_state.registro_sostituzioni:
    df_reg = pd.DataFrame(st.session_state.registro_sostituzioni)
    st.dataframe(df_reg, use_container_width=True)
    
    st.subheader("📈 Riepilogo Conteggi per Docente (DISP vs EXTRA)")
    summary = df_reg.groupby(['Docente', 'Tipo']).size().unstack(fill_value=0)
    st.bar_chart(summary)
else:
    st.info("Nessuna sostituzione ancora registrata per l'anno scolastico in corso.")
