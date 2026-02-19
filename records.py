import json
import os

RECORD_FILE = "records.json"

def load_records():
    """Devuelve la lista de récords guardados, ordenada de mayor a menor score."""
    if not os.path.exists(RECORD_FILE):
        return []
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def save_record(name, score, distance):
    """
    Guarda el récord del jugador:
    - Mantiene nombre, score y distancia.
    - Si un mismo jugador tiene un score menor, se reemplaza.
    - Ordena de mayor a menor score y guarda top 10.
    """
    records = load_records()

    # Revisar si ya existe un récord de este jugador
    updated = False
    for rec in records:
        if rec["name"] == name:
            if score > rec["score"]:
                rec["score"] = score
                rec["distance"] = distance
            updated = True
            break

    if not updated:
        records.append({"name": name, "score": score, "distance": distance})

    # Ordenar de mayor a menor score
    records.sort(key=lambda r: r["score"], reverse=True)

    # Guardar solo los top 10
    records = records[:10]

    try:
        with open(RECORD_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_top_records(n=10):
    """Devuelve los top n récords ordenados por score."""
    records = load_records()
    return records[:n]
