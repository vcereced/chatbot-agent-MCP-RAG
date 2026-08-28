import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

# CONFIGURACIÓN DEL TEST DE ESTRÉS
TOTAL_CONVERSATIONS = 200  # Número de hilos concurrentes
MESSAGES_PER_CONV = 5     # Mensajes a enviar por conversación


def make_post_request(url: str, payload: dict) -> tuple[bool, dict | str]:
    """Realiza un POST HTTP síncrono usando urllib nativo."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            return True, json.loads(res_body)
    except Exception as e:
        return False, str(e)


def simulate_user_session(session_id: int):
    """Simula el flujo completo de un usuario."""
    # 1. Crear conversación
    ok, res = make_post_request(
        f"{BASE_URL}/conversations/get_or_create",
        {"conversation_id": None}
    )
    if not ok:
        return False, f"Err /get_or_create: {res}"

    conv = res["conversation"]

    # 2. Enviar mensajes
    for i in range(MESSAGES_PER_CONV):
        conv["messages"].append({
            "role": "user",
            "content": f"Mensaje {i} de la sesión {session_id}"
        })
        
        ok_save, res_save = make_post_request(
            f"{BASE_URL}/conversations/save",
            {"conversation": conv}
        )
        if not ok_save:
            return False, f"Err /save: {res_save}"

    return True, "OK"


def run_stress_test():
    total_requests = TOTAL_CONVERSATIONS * (1 + MESSAGES_PER_CONV)
    print(f"🚀 Iniciando prueba de carga masiva (Módulos Nativos):")
    print(f"   • {TOTAL_CONVERSATIONS} conversaciones en paralelo")
    print(f"   • {total_requests} peticiones HTTP totales\n")

    start_time = time.time()

    # Usamos un ThreadPool para enviar peticiones en paralelo sin librerías externas
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(simulate_user_session, range(TOTAL_CONVERSATIONS)))

    elapsed_time = time.time() - start_time

    # Métricas
    successes = sum(1 for ok, _ in results if ok)
    failures = sum(1 for ok, _ in results if not ok)
    rps = total_requests / elapsed_time

    print("=" * 45)
    print("📊 RESULTADOS DEL TEST DE ESTRÉS")
    print("=" * 45)
    print(f"⏱️  Tiempo total:          {elapsed_time:.2f} segundos")
    print(f"⚡ Peticiones/segundo:    {rps:.2f} Req/sec")
    print(f"✅ Sesiones completadas:  {successes} / {TOTAL_CONVERSATIONS}")
    print(f"❌ Fallos detectados:     {failures}")

    if failures > 0:
        print("\n⚠️ Muestra de errores:")
        errors = set(msg for ok, msg in results if not ok)
        for err in list(errors)[:5]:
            print(f"  - {err}")


if __name__ == "__main__":
    run_stress_test()