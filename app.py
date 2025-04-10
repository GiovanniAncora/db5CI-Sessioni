import pymysql.cursors
from flask import Flask, render_template, session, request, redirect, url_for

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='24082006', database='db5CI')
cursore = conn.cursor()

# cursore.execute('SHOW COLUMNS FROM verifiche;')
# print(cursore.fetchall())

app = Flask(__name__)

app.secret_key = 'provola1234'


@app.route('/')
def index():
    query = 'SELECT matricola, nome, cognome, data_nascita FROM alunni'
    cursore.execute(query)
    risultato = cursore.fetchall()
    return render_template('index.html', alunni= risultato, campi= cursore.description)

@app.route('/voti/<studente>')
def voti(studente):
    if 'username' in session:
        print(studente)

        queryControlloMatr = "SELECT matr FROM utenti WHERE username = %s;"
        cursore.execute(queryControlloMatr, (session['username'],))
        matr = str(cursore.fetchall()[0][0])

        print(type(studente), type(matr), studente == matr)
        if studente == matr:
            queryVoti = 'SELECT * FROM verifiche WHERE studente = %s'
            cursore.execute(queryVoti, (studente,))
            risultatoVoti = cursore.fetchall()
            return render_template("voti.html", voti=risultatoVoti, campi= cursore.description)
        else:
            print('Non hai l\'accesso a QUESTA pagina.')
            print(session['username'], matr)
            return redirect(url_for('voti', studente=matr))

    else:
        print('Fai l\'accesso')
        return redirect(url_for('login'))

@app.route('/medie')
def medie():
    queryMedie = 'SELECT cognome, nome, AVG(voto) AS media FROM alunni, verifiche WHERE alunni.matricola = verifiche.studente GROUP BY studente'
    cursore.execute(queryMedie)
    risultatoMedie = cursore.fetchall()
    # print(risultatoMedie)
    return render_template("medie.html", medie=risultatoMedie, campi= cursore.description)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        codice = request.form['codice']

        queryUtente = 'SELECT * FROM utenti WHERE username=%s;'
        cursore.execute(queryUtente, (username,))
        ris = cursore.fetchall()
        print(ris)
        if ris:
            if ris[0][1] == codice:
                session['username'] = username
                session['codice'] = codice
                # print(f'Login effettuato come {session["username"]}: {session["codice"]}')
                # print(type(session['username']))
                return redirect(url_for('voti', studente= ris[0][2]))
            else:
                print('Password non corretta.')
                return redirect(url_for('login'))
        else:
            print('Username non esistente.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        matricola = request.form['matricola']

        queryControllo = 'SELECT * FROM utenti WHERE username = %s;'
        cursore.execute(queryControllo, (username,))
        ris = cursore.fetchall()

        if ris:
            print("L'username esiste già.")
            return redirect(url_for('register'))
        
        queryControlloMatr = 'SELECT matricola FROM alunni WHERE matricola = %s;'
        cursore.execute(queryControlloMatr, (matricola,))
        
        if not cursore.fetchall():
            print('La matricola non esiste.')
            return redirect(url_for('register'))
        
        queryInserimento = "INSERT INTO utenti VALUES (%s, %s, %s);"
        cursore.execute(queryInserimento, (username, password, matricola))
        conn.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('codice', None)
    return redirect(url_for('index'))

app.run(debug=True)