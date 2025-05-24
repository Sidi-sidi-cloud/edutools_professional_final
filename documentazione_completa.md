# Documentazione EduTools Professional

## Panoramica
EduTools Professional è una suite completa di strumenti per docenti che integra:
- **Assistente Docente**: Un chatbot AI che risponde a qualsiasi domanda sulla didattica
- **Valutazione RIZA**: Strumento per la valutazione formativa basata sui processi RIZA
- **Pannello Amministratore**: Dashboard completa per la gestione utenti e monitoraggio

La piattaforma è stata completamente riprogettata con un'interfaccia professionale, menu laterale fisso e layout responsive per desktop e mobile.

## Installazione e Configurazione

### Requisiti
- Python 3.8 o superiore
- Pip (gestore pacchetti Python)
- Chiave API OpenAI valida

### Passi per l'installazione
1. Estrai il file `edutools_professional.zip` in una directory
2. Crea un ambiente virtuale Python:
   ```
   python -m venv venv
   ```
3. Attiva l'ambiente virtuale:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```
5. Configura il file `.env`:
   - Copia `.env.example` in `.env`
   - Inserisci la tua chiave API OpenAI
   - Modifica altre impostazioni se necessario
6. Inizializza il database (se non già presente):
   ```
   cd data
   python create_admin_db.py
   ```
7. Avvia l'applicazione:
   ```
   python app.py
   ```

### Configurazione per il deploy su Render
1. Accedi a [Render](https://render.com)
2. Crea un nuovo Web Service
3. Collega il tuo repository GitHub
4. Configura le variabili d'ambiente (copia i valori dal file `.env`)
5. Imposta il comando di avvio: `gunicorn app:app`

## Struttura dell'Applicazione

### Interfaccia Utente
- **Home**: Dashboard principale con accesso a tutti gli strumenti
- **Assistente Docente**: Chatbot AI per supporto didattico
- **Valutazione RIZA**: Strumento per inserire e classificare osservazioni

### Pannello Amministratore
- **Dashboard**: Panoramica delle statistiche di utilizzo
- **Gestione Utenti**: Creazione, modifica ed eliminazione utenti
- **Conversazioni**: Monitoraggio di tutte le interazioni con l'AI
- **Analisi Utilizzo**: Statistiche dettagliate sull'utilizzo della piattaforma
- **Impostazioni**: Configurazione generale dell'applicazione

## Funzionalità Principali

### Assistente Docente
- Risponde a domande su didattica, gestione classe, comunicazione con genitori
- Suggerisce attività didattiche e strategie di insegnamento
- Mantiene la cronologia delle conversazioni
- Offre suggerimenti contestuali per domande correlate

### Valutazione RIZA
- Inserimento osservazioni qualitative degli allievi
- Suggerimenti automatici per la classificazione secondo il modello RIZA
- Visualizzazione e gestione delle osservazioni salvate
- Supporto per diverse discipline e ambiti

### Pannello Amministratore
- Monitoraggio in tempo reale dell'utilizzo della piattaforma
- Gestione completa degli utenti con diversi ruoli e permessi
- Accesso a tutte le conversazioni degli utenti
- Analisi dettagliate sull'utilizzo degli strumenti
- Esportazione dati per reportistica

## Sicurezza e Privacy

### Gestione delle Chiavi API
- **IMPORTANTE**: Non caricare MAI il file `.env` su GitHub o altri repository pubblici
- La chiave API OpenAI deve essere mantenuta riservata
- In ambiente di produzione, utilizzare variabili d'ambiente del server

### Protezione dei Dati
- Le conversazioni sono archiviate nel database locale
- L'accesso al pannello amministratore è protetto da autenticazione
- I dati sensibili non vengono mai esposti nelle URL o nei log

## Accesso e Credenziali

### Utenti Demo
L'applicazione include alcuni utenti di esempio:

| Nome | Email | Password | Ruolo |
|------|-------|----------|-------|
| Admin Sistema | admin@edutools.it | admin123 | admin |
| Marco Rossi | marco.rossi@scuola.edu | password123 | docente |
| Laura Bianchi | laura.bianchi@scuola.edu | password123 | docente |
| Giovanni Verdi | giovanni.verdi@scuola.edu | password123 | coordinatore |

**Nota**: In un ambiente di produzione, modificare immediatamente queste password.

## Personalizzazione

### Interfaccia Grafica
- I file CSS si trovano in `static/css/`
- Il file principale per lo stile è `professional.css`
- Le icone utilizzano Bootstrap Icons

### Funzionalità AI
- Modifica il file `.env` per cambiare il modello AI utilizzato
- Personalizza i prompt di sistema in `app.py` per adattare le risposte dell'AI

## Risoluzione Problemi

### Errori Comuni
- **Errore API Key**: Verifica che la chiave API OpenAI sia corretta nel file `.env`
- **Database non trovato**: Assicurati di aver eseguito `create_admin_db.py`
- **Porta già in uso**: Cambia la porta in `app.py` (ultima riga)

### Supporto
Per assistenza tecnica, contattare il supporto all'indirizzo support@edutools.it

## Aggiornamenti Futuri
- Integrazione con sistemi di gestione scolastica
- Esportazione delle valutazioni in formato standard
- Dashboard personalizzabili per diversi ruoli
- Supporto per più lingue

---

© 2025 EduTools - Tutti i diritti riservati
