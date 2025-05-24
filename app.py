import os
import sqlite3
import json
import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import openai

# Carica le variabili d'ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chiave_segreta_predefinita')

# Configurazione OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.3))
ENABLE_AI = os.getenv('ENABLE_AI', 'True').lower() == 'true'

# Percorsi database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'riza.db')
ADMIN_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'admin.db')

# Funzione per ottenere connessione al database RIZA
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Funzione per ottenere connessione al database Admin
def get_admin_db_connection():
    conn = sqlite3.connect(ADMIN_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Funzione per registrare attività utente
def log_activity(user_id, user_name, activity_type, details=None):
    try:
        conn = get_admin_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        details_json = json.dumps(details) if details else None
        
        cursor.execute(
            "INSERT INTO activities (user_id, user_name, activity_type, details, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, user_name, activity_type, details_json, timestamp)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Errore durante il log dell'attività: {e}")

# Middleware per verificare l'autenticazione
@app.before_request
def check_auth():
    # Escludi le pagine che non richiedono autenticazione
    excluded_routes = ['login', 'static']
    if request.endpoint in excluded_routes:
        return
    
    # Se l'utente non è autenticato, reindirizza al login
    if 'user_id' not in session and request.endpoint != 'login':
        return redirect(url_for('login'))

# Rotte per l'autenticazione
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_admin_db_connection()
        cursor = conn.cursor()
        
        user = cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        
        conn.close()
        
        if user and user['password'] == password:  # In produzione usare password hashate
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            
            # Log attività
            log_activity(user['id'], user['name'], 'login')
            
            return redirect(url_for('home'))
        else:
            error = 'Credenziali non valide. Riprova.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'logout')
    
    session.clear()
    return redirect(url_for('login'))

# Rotte principali
@app.route('/')
def home():
    if 'user_id' in session:
        log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'home'})
    
    return render_template('home.html')

@app.route('/chatbot')
def chatbot():
    if 'user_id' in session:
        log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'chatbot'})
    
    return render_template('chatbot.html')

@app.route('/valutazione')
def valutazione():
    conn = get_db_connection()
    discipline = [row['disciplina'] for row in conn.execute("SELECT DISTINCT disciplina FROM aree_disciplinari").fetchall()]
    conn.close()
    
    if 'user_id' in session:
        log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'valutazione'})
    
    return render_template('index.html', discipline=discipline)

@app.route('/view_observations')
def view_observations():
    conn = get_db_connection()
    
    # Parametri di ricerca
    allievo = request.args.get('allievo', '')
    classe = request.args.get('classe', '')
    disciplina = request.args.get('disciplina', '')
    dimensione = request.args.get('dimensione', '')
    
    # Costruisci la query in base ai parametri
    query = """
        SELECT o.id, o.allievo, o.classe, o.disciplina, o.situazione, o.osservazione, 
               o.dimensione, o.processo, o.livello, o.data_creazione, o.id_descrittore
        FROM osservazioni o
        WHERE 1=1
    """
    params = []
    
    if allievo:
        query += " AND o.allievo LIKE ?"
        params.append(f"%{allievo}%")
    
    if classe:
        query += " AND o.classe LIKE ?"
        params.append(f"%{classe}%")
    
    if disciplina:
        query += " AND o.disciplina = ?"
        params.append(disciplina)
    
    if dimensione:
        query += " AND o.dimensione = ?"
        params.append(dimensione)
    
    query += " ORDER BY o.data_creazione DESC"
    
    # Esegui la query
    observations = conn.execute(query, params).fetchall()
    
    # Ottieni elenchi per i filtri
    discipline = [row['disciplina'] for row in conn.execute("SELECT DISTINCT disciplina FROM aree_disciplinari").fetchall()]
    dimensioni = [row['dimensione_riza'] for row in conn.execute("SELECT DISTINCT dimensione_riza FROM descrittori").fetchall()]
    
    conn.close()
    
    if 'user_id' in session:
        log_activity(
            session['user_id'], 
            session.get('user_name', 'Unknown'), 
            'search_observations', 
            {
                'allievo': allievo,
                'classe': classe,
                'disciplina': disciplina,
                'dimensione': dimensione,
                'results_count': len(observations)
            }
        )
    
    return render_template(
        'view_observations.html', 
        observations=observations, 
        discipline=discipline, 
        dimensioni=dimensioni
    )

@app.route('/get_observation_details/<int:observation_id>')
def get_observation_details(observation_id):
    try:
        conn = get_db_connection()
        
        # Ottieni i dettagli dell'osservazione
        observation = conn.execute(
            """
            SELECT o.*, d.testo_descrittore
            FROM osservazioni o
            LEFT JOIN descrittori d ON o.id_descrittore = d.id
            WHERE o.id = ?
            """,
            (observation_id,)
        ).fetchone()
        
        conn.close()
        
        if observation:
            # Converti l'oggetto Row in dizionario
            observation_dict = dict(observation)
            
            if 'user_id' in session:
                log_activity(
                    session['user_id'], 
                    session.get('user_name', 'Unknown'), 
                    'view_observation_details', 
                    {'observation_id': observation_id}
                )
            
            return jsonify({'success': True, 'observation': observation_dict})
        else:
            return jsonify({'success': False, 'error': 'Osservazione non trovata'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chatbot_query', methods=['POST'])
def chatbot_query():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'response': 'Nessuna domanda ricevuta. Come posso aiutarti?'})
    
    try:
        if ENABLE_AI and openai.api_key:
            # Usa OpenAI per generare la risposta
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un assistente esperto in ambito educativo e didattico, specializzato nel supporto ai docenti. Fornisci risposte dettagliate, pratiche e basate su evidenze scientifiche. Quando possibile, offri esempi concreti e suggerimenti applicabili in classe."},
                    {"role": "user", "content": query}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content
            
            # Genera suggerimenti correlati
            suggestions_response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "Genera 5 domande correlate che un docente potrebbe voler fare dopo aver ricevuto una risposta alla sua domanda iniziale. Fornisci solo le domande, una per riga, senza numerazione o punti elenco."},
                    {"role": "user", "content": f"Domanda iniziale: {query}\nRisposta ricevuta: {ai_response}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            suggestions_text = suggestions_response.choices[0].message.content
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
            
            if 'user_id' in session:
                log_activity(
                    session['user_id'], 
                    session.get('user_name', 'Unknown'), 
                    'chatbot_query', 
                    {'query': query, 'response_length': len(ai_response)}
                )
            
            return jsonify({'response': ai_response, 'suggestions': suggestions})
        
        else:
            # Risposta predefinita se OpenAI non è configurato
            return jsonify({
                'response': 'Mi dispiace, il servizio AI non è attualmente disponibile. Controlla la configurazione API o contatta l\'amministratore.',
                'suggestions': [
                    'Come posso configurare l\'API OpenAI?',
                    'Quali sono le alternative all\'utilizzo di OpenAI?',
                    'Come posso ottenere una chiave API?'
                ]
            })
    
    except Exception as e:
        print(f"Errore nell'elaborazione della query chatbot: {e}")
        return jsonify({
            'response': f'Mi dispiace, si è verificato un errore durante l\'elaborazione della tua richiesta. Dettaglio tecnico: {str(e)}',
            'suggestions': [
                'Potresti riprovare con una domanda più semplice?',
                'Come posso formulare meglio le mie domande?',
                'Quali sono gli argomenti su cui posso chiedere supporto?'
            ]
        })

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    data = request.json
    osservazione = data.get('osservazione', '')
    disciplina = data.get('disciplina', '')
    
    if not osservazione or not disciplina:
        return jsonify({'suggestions': []})
    
    try:
        conn = get_db_connection()
        
        # Ottieni i descrittori per la disciplina selezionata
        descrittori = conn.execute(
            """
            SELECT d.*, a.disciplina
            FROM descrittori d
            JOIN aree_disciplinari a ON d.area_disciplinare_id = a.id
            WHERE a.disciplina = ?
            """,
            (disciplina,)
        ).fetchall()
        
        conn.close()
        
        if ENABLE_AI and openai.api_key:
            # Usa OpenAI per analizzare l'osservazione e trovare corrispondenze
            try:
                prompt = f"""
                Analizza la seguente osservazione di un allievo e identifica quali descrittori RIZA sono più pertinenti.
                
                Osservazione: "{osservazione}"
                
                Disciplina: {disciplina}
                
                Descrittori disponibili:
                """
                
                for d in descrittori[:15]:  # Limitiamo a 15 descrittori per non superare i limiti di token
                    prompt += f"\nID: {d['id']} - Dimensione: {d['dimensione_riza']} - Processo: {d['processo_specifico_verbo']} - Livello: {d['livello']} - Descrittore: {d['testo_descrittore']}"
                
                prompt += """
                
                Restituisci i 3 descrittori più pertinenti all'osservazione in formato JSON con la seguente struttura:
                [
                  {
                    "id": "ID del descrittore",
                    "similarita": "valore da 0 a 1 che indica quanto è pertinente",
                    "spiegazione": "breve spiegazione del perché questo descrittore è pertinente all'osservazione"
                  },
                  ...
                ]
                
                Includi solo il JSON nella tua risposta, senza testo aggiuntivo.
                """
                
                response = openai.ChatCompletion.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": "Sei un assistente specializzato in valutazione formativa e nel modello RIZA (Risorse, Interpretazione, Azione, Autoregolazione). Il tuo compito è analizzare osservazioni di allievi e collegarle ai descrittori RIZA più pertinenti."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=MAX_TOKENS,
                    temperature=0.2
                )
                
                ai_response = response.choices[0].message.content
                
                # Estrai il JSON dalla risposta
                import re
                json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                if json_match:
                    ai_suggestions = json.loads(json_match.group(0))
                else:
                    # Tentativo alternativo se il primo metodo fallisce
                    try:
                        ai_suggestions = json.loads(ai_response)
                    except:
                        # Fallback al metodo TF-IDF se non riusciamo a estrarre JSON
                        ai_suggestions = []
                
                # Se abbiamo ottenuto suggerimenti da AI, arricchiscili con i dati completi
                if ai_suggestions:
                    suggestions = []
                    for sugg in ai_suggestions:
                        desc_id = sugg.get('id')
                        for d in descrittori:
                            if str(d['id']) == str(desc_id):
                                suggestion = dict(d)
                                suggestion['similarita'] = float(sugg.get('similarita', 0.5))
                                suggestion['spiegazione'] = sugg.get('spiegazione', '')
                                suggestions.append(suggestion)
                                break
                    
                    # Ordina per similarità decrescente
                    suggestions.sort(key=lambda x: x['similarita'], reverse=True)
                    
                    if 'user_id' in session:
                        log_activity(
                            session['user_id'], 
                            session.get('user_name', 'Unknown'), 
                            'get_suggestions', 
                            {'osservazione': osservazione, 'disciplina': disciplina, 'method': 'ai', 'count': len(suggestions)}
                        )
                    
                    return jsonify({'suggestions': [dict(s) for s in suggestions]})
            
            except Exception as e:
                print(f"Errore nell'elaborazione AI: {e}")
                # In caso di errore, fallback al metodo TF-IDF
                pass
        
        # Metodo TF-IDF (fallback o se AI non è abilitata)
        # Prepara i testi per l'analisi
        testi_descrittori = [d['testo_descrittore'] for d in descrittori]
        
        # Crea il vettorizzatore TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(testi_descrittori + [osservazione])
        
        # Calcola la similarità del coseno
        cosine_similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1]).flatten()
        
        # Ottieni gli indici dei descrittori più simili
        top_indices = cosine_similarities.argsort()[-5:][::-1]
        
        # Prepara i suggerimenti
        suggestions = []
        for idx in top_indices:
            if cosine_similarities[idx] > 0:  # Solo se c'è una similarità positiva
                suggestion = dict(descrittori[idx])
                suggestion['similarita'] = float(cosine_similarities[idx])
                suggestions.append(suggestion)
        
        if 'user_id' in session:
            log_activity(
                session['user_id'], 
                session.get('user_name', 'Unknown'), 
                'get_suggestions', 
                {'osservazione': osservazione, 'disciplina': disciplina, 'method': 'tfidf', 'count': len(suggestions)}
            )
        
        return jsonify({'suggestions': [dict(s) for s in suggestions]})
    
    except Exception as e:
        print(f"Errore nell'elaborazione dei suggerimenti: {e}")
        return jsonify({'error': str(e), 'suggestions': []})

@app.route('/save_observation', methods=['POST'])
def save_observation():
    data = request.json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Inserisci l'osservazione nel database
        cursor.execute(
            """
            INSERT INTO osservazioni (
                allievo, classe, disciplina, situazione, osservazione,
                dimensione, processo, livello, id_descrittore, data_creazione
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                data.get('allievo'),
                data.get('classe'),
                data.get('disciplina'),
                data.get('situazione'),
                data.get('osservazione'),
                data.get('dimensione'),
                data.get('processo'),
                data.get('livello'),
                data.get('id_descrittore')
            )
        )
        
        conn.commit()
        observation_id = cursor.lastrowid
        conn.close()
        
        if 'user_id' in session:
            log_activity(
                session['user_id'], 
                session.get('user_name', 'Unknown'), 
                'save_observation', 
                {
                    'observation_id': observation_id,
                    'allievo': data.get('allievo'),
                    'classe': data.get('classe'),
                    'disciplina': data.get('disciplina')
                }
            )
        
        return jsonify({'success': True, 'id': observation_id})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Rotte amministrative
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        return redirect(url_for('home'))
    
    try:
        conn = get_admin_db_connection()
        
        # Statistiche utenti
        user_stats = {
            'total_users': conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count'],
            'docenti': conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'docente'").fetchone()['count'],
            'coordinatori': conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'coordinatore'").fetchone()['count'],
            'admin': conn.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'").fetchone()['count']
        }
        
        # Statistiche conversazioni per tool
        conversation_stats = conn.execute(
            """
            SELECT activity_type as tool, COUNT(*) as count
            FROM activities
            WHERE activity_type IN ('chatbot_query', 'get_suggestions')
            GROUP BY activity_type
            """
        ).fetchall()
        
        # Statistiche attività
        activity_stats = conn.execute(
            """
            SELECT activity_type, COUNT(*) as count
            FROM activities
            GROUP BY activity_type
            """
        ).fetchall()
        
        # Attività recenti
        recent_activities = conn.execute(
            """
            SELECT * FROM activities
            ORDER BY timestamp DESC
            LIMIT 20
            """
        ).fetchall()
        
        # Attività giornaliere
        daily_activities = conn.execute(
            """
            SELECT strftime('%Y-%m-%d', timestamp) as day, COUNT(*) as count
            FROM activities
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
            """
        ).fetchall()
        
        conn.close()
        
        if 'user_id' in session:
            log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'admin_dashboard'})
        
        return render_template(
            'admin_dashboard.html',
            user_stats=user_stats,
            conversation_stats=conversation_stats,
            activity_stats=activity_stats,
            recent_activities=recent_activities,
            daily_activities=daily_activities
        )
    
    except Exception as e:
        return f"Errore: {e}"

@app.route('/admin/users')
def admin_users():
    if session.get('user_role') != 'admin':
        return redirect(url_for('home'))
    
    try:
        conn = get_admin_db_connection()
        users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        conn.close()
        
        if 'user_id' in session:
            log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'admin_users'})
        
        return render_template('admin_users.html', users=users)
    
    except Exception as e:
        return f"Errore: {e}"

@app.route('/admin/conversations')
def admin_conversations():
    if session.get('user_role') != 'admin':
        return redirect(url_for('home'))
    
    try:
        conn = get_admin_db_connection()
        
        # Ottieni le conversazioni (attività di tipo chatbot_query)
        conversations = conn.execute(
            """
            SELECT * FROM activities
            WHERE activity_type = 'chatbot_query'
            ORDER BY timestamp DESC
            LIMIT 100
            """
        ).fetchall()
        
        conn.close()
        
        if 'user_id' in session:
            log_activity(session['user_id'], session.get('user_name', 'Unknown'), 'page_view', {'page': 'admin_conversations'})
        
        return render_template('admin_conversations.html', conversations=conversations)
    
    except Exception as e:
        return f"Errore: {e}"

# API amministrative
@app.route('/admin/api/users', methods=['POST', 'PUT', 'DELETE'])
def admin_api_users():
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'error': 'Accesso non autorizzato'})
    
    try:
        conn = get_admin_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            # Crea nuovo utente
            data = request.json
            
            # Verifica se l'email esiste già
            existing_user = cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (data.get('email'),)
            ).fetchone()
            
            if existing_user:
                return jsonify({'success': False, 'error': 'Email già in uso'})
            
            cursor.execute(
                """
                INSERT INTO users (name, email, password, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    data.get('name'),
                    data.get('email'),
                    data.get('password'),
                    data.get('role', 'docente'),
                    data.get('status', 'attivo')
                )
            )
            
            conn.commit()
            user_id = cursor.lastrowid
            
            log_activity(
                session['user_id'], 
                session.get('user_name', 'Unknown'), 
                'create_user', 
                {'user_id': user_id, 'name': data.get('name'), 'role': data.get('role')}
            )
            
            return jsonify({'success': True, 'id': user_id})
        
        elif request.method == 'PUT':
            # Aggiorna utente esistente
            data = request.json
            user_id = data.get('id')
            
            if not user_id:
                return jsonify({'success': False, 'error': 'ID utente mancante'})
            
            # Costruisci la query di aggiornamento
            update_fields = []
            params = []
            
            if 'name' in data:
                update_fields.append("name = ?")
                params.append(data['name'])
            
            if 'email' in data:
                update_fields.append("email = ?")
                params.append(data['email'])
            
            if 'password' in data and data['password']:
                update_fields.append("password = ?")
                params.append(data['password'])
            
            if 'role' in data:
                update_fields.append("role = ?")
                params.append(data['role'])
            
            if 'status' in data:
                update_fields.append("status = ?")
                params.append(data['status'])
            
            if not update_fields:
                return jsonify({'success': False, 'error': 'Nessun campo da aggiornare'})
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            params.append(user_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            log_activity(
                session['user_id'], 
                session.get('user_name', 'Unknown'), 
                'update_user', 
                {'user_id': user_id, 'updated_fields': list(data.keys())}
            )
            
            return jsonify({'success': True})
        
        elif request.method == 'DELETE':
            # Elimina utente
            data = request.json
            user_id = data.get('id')
            
            if not user_id:
                return jsonify({'success': False, 'error': 'ID utente mancante'})
            
            # Verifica se l'utente esiste
            user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user:
                return jsonify({'success': False, 'error': 'Utente non trovato'})
            
            # Non permettere l'eliminazione dell'ultimo admin
            if user['role'] == 'admin':
                admin_count = cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'").fetchone()['count']
                if admin_count <= 1:
                    return jsonify({'success': False, 'error': 'Impossibile eliminare l\'ultimo amministratore'})
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            
            log_activity(
                session['user_id'], 
                session.get('user_name', 'Unknown'), 
                'delete_user', 
                {'user_id': user_id}
            )
            
            return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
