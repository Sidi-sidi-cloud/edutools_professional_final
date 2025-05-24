# Documentazione EduTools - Suite Multi-Tool per Docenti

## Introduzione
EduTools è una suite di strumenti progettata per supportare i docenti nelle loro attività quotidiane. Integra due potenti strumenti basati su intelligenza artificiale:

1. **Assistente Docente**: Un chatbot educativo che risponde a qualsiasi domanda relativa all'attività di insegnamento
2. **Valutazione RIZA**: Lo strumento originale per la valutazione formativa basata sui processi RIZA

## Accesso all'applicazione
L'applicazione è accessibile all'URL:
https://5000-iud8y07ukma1ecpg7sctp-97f7cde9.manus.computer

## Funzionalità principali

### Assistente Docente
- Risponde a domande su metodologie didattiche, creazione di attività, gestione della classe
- Fornisce consigli per la comunicazione con genitori e colleghi
- Suggerisce strategie per motivare gli studenti e gestire situazioni problematiche
- Genera suggerimenti di follow-up pertinenti per approfondire gli argomenti

### Valutazione RIZA
- Permette l'inserimento di osservazioni qualitative degli allievi
- Analizza il testo e propone collegamenti ai processi RIZA
- Salva e visualizza le osservazioni classificate
- Utilizza l'AI per generare suggerimenti più accurati e pertinenti

## Configurazione dell'API OpenAI
L'applicazione utilizza l'API di OpenAI per entrambi gli strumenti. La configurazione può essere gestita tramite file `.env`:

1. Crea un file `.env` nella directory principale dell'applicazione
2. Aggiungi la seguente riga: `OPENAI_API_KEY=your_api_key_here`
3. Puoi configurare anche altri parametri come mostrato nel file `.env.example`

## Istruzioni per l'uso

### Navigazione
- Dalla home page, puoi accedere a entrambi gli strumenti tramite i pulsanti "Accedi"
- Il menu di navigazione in alto permette di passare da uno strumento all'altro in qualsiasi momento

### Utilizzo dell'Assistente Docente
1. Clicca su "Assistente Docente" nel menu o sulla home page
2. Digita la tua domanda nel campo di testo in fondo alla chat
3. Premi il pulsante di invio (icona freccia) o premi Enter
4. Ricevi la risposta dell'assistente
5. Puoi anche selezionare uno dei suggerimenti predefiniti o di follow-up

### Utilizzo della Valutazione RIZA
1. Clicca su "Valutazione RIZA" nel menu o sulla home page
2. Compila i campi richiesti (Classe, Allievo, Disciplina, Osservazione)
3. Clicca su "Ottieni Suggerimenti"
4. Seleziona il suggerimento più appropriato
5. Clicca su "Salva Osservazione"

## Requisiti tecnici
- Browser web moderno (Chrome, Firefox, Safari, Edge)
- Connessione internet
- Chiave API OpenAI (per funzionalità AI complete)

## Pubblicazione su Render
L'applicazione è già configurata per essere pubblicata su Render. Per aggiornare o ripubblicare:

1. Assicurati che il repository GitHub sia aggiornato
2. Accedi al tuo account Render
3. Collega il repository GitHub
4. Configura le variabili d'ambiente (OPENAI_API_KEY)
5. Avvia il deploy

## Personalizzazione
L'applicazione può essere facilmente personalizzata:

- Modifica i file HTML in `/templates` per cambiare l'interfaccia
- Aggiorna i file CSS in `/static/css` per modificare lo stile
- Personalizza i prompt AI in `app.py` per adattare le risposte alle tue esigenze

## Limitazioni attuali
- L'applicazione utilizza SQLite, adatto per prototipi ma non per uso intensivo
- Il piano gratuito di Render può mettere in pausa il servizio dopo periodi di inattività
- Le risposte AI dipendono dalla qualità della chiave API e dal modello utilizzato

## Sviluppi futuri
- Integrazione di ulteriori strumenti educativi
- Miglioramento dell'interfaccia utente
- Aggiunta di funzionalità di reportistica
- Supporto per più lingue

## Supporto
Per problemi o domande, contatta il supporto tecnico o consulta la documentazione di OpenAI per questioni relative all'API.
