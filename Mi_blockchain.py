#!/usr/bin/env python3
import time
import json
import hashlib
import logging
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API de la blockchain y parámetros de minería
BLOCKCHAIN_API_URL = os.getenv("BLOCKCHAIN_API_URL", "https://8d04-2-137-118-154.ngrok-free.app:5000")
BLOCK_TIME = int(os.getenv("BLOCK_TIME", 10))
DIFFICULTY = int(os.getenv("MINING_DIFFICULTY", 4))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_chain():
    try:
        response = requests.get(f"{BLOCKCHAIN_API_URL}/chain")
        if response.status_code == 200:
            return response.json()["chain"]
        else:
            logging.error("Error al obtener la cadena: " + response.text)
            return None
    except Exception as e:
        logging.error("Error conectando con la blockchain: " + str(e))
        return None

def get_pending_transactions():
    try:
        response = requests.get(f"{BLOCKCHAIN_API_URL}/pending_transactions")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error("Error al obtener transacciones pendientes: " + response.text)
            return []
    except Exception as e:
        logging.error("Error conectando con la blockchain: " + str(e))
        return []

def calculate_hash(index, transactions, timestamp, previous_hash, nonce):
    block_data = {
        "index": index,
        "transactions": transactions,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
        "nonce": nonce
    }
    block_string = json.dumps(block_data, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def propose_block(block):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{BLOCKCHAIN_API_URL}/propose_block", headers=headers, data=json.dumps(block))
        if response.status_code == 201:
            logging.info("Bloque propuesto exitosamente: " + response.text)
        else:
            logging.error("Error al proponer el bloque: " + response.text)
    except Exception as e:
        logging.error("Error al enviar el bloque: " + str(e))

def mine_block():
    chain = get_chain()
    if not chain:
        logging.error("No se pudo obtener la cadena. Abortar minería.")
        return
    last_block = chain[-1]
    index = last_block["index"] + 1
    previous_hash = last_block["hash"]
    transactions = get_pending_transactions()  # Pueden estar vacías
    timestamp = time.time()
    nonce = 0

    logging.info("Iniciando prueba de trabajo...")
    while True:
        block_hash = calculate_hash(index, transactions, timestamp, previous_hash, nonce)
        if block_hash.startswith("0" * DIFFICULTY):
            logging.info(f"Bloque minado: nonce={nonce}, hash={block_hash}")
            break
        nonce += 1

    block = {
        "index": index,
        "transactions": transactions,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
        "nonce": nonce,
        "hash": block_hash
    }
    propose_block(block)

def mining_loop():
    while True:
        mine_block()
        time.sleep(BLOCK_TIME)

if __name__ == "__main__":
    logging.info("Iniciando el proceso de minería...")
    mining_loop()
