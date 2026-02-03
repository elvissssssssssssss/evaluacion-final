from utils import Estado, invoke_llm
from langgraph.graph import StateGraph, START, END

# Nombre exacto del modelo según tu imagen
MODELO = "llama3.2"

def nodo_1(estado: Estado) -> Estado:
    prompt = "Responde a este mensaje en español: " + estado["mensaje"]
    respuesta = invoke_llm(MODELO, prompt, streaming=True, print_label="nodo_1: ")
    return {"mensaje": respuesta}

def nodo_2(estado: Estado) -> Estado:
    prompt = "Resume este texto en español: " + estado["mensaje"]
    respuesta = invoke_llm(MODELO, prompt, streaming=True, print_label="nodo_2: ")
    return {"mensaje": respuesta}

def nodo_3(estado: Estado) -> Estado:
    prompt = "Analiza el sentimiento de este texto en español (positivo, negativo, neutral): " + estado["mensaje"]
    respuesta = invoke_llm(MODELO, prompt, streaming=True, print_label="nodo_3: ")
    return {"sentimiento": respuesta}

def main():
    # Crear el grafo
    constructor = StateGraph(Estado)

    # Agregar nodos
    constructor.add_node("nodo_1", nodo_1)
    constructor.add_node("nodo_2", nodo_2)
    constructor.add_node("nodo_3", nodo_3)

    # Agregar aristas
    constructor.add_edge(START, "nodo_1")
    constructor.add_edge("nodo_1", "nodo_2")
    constructor.add_edge("nodo_2", "nodo_3")
    constructor.add_edge("nodo_3", END) # Conexión final necesaria

    # Compilar el grafo
    grafo = constructor.compile()

    print(f"--- Sistema iniciado usando {MODELO}. Escribe 'salir' para terminar ---")
    while True:
        try:
            mensaje = input(">>> ")
        except EOFError:
            break
            
        if mensaje.lower() == "salir":
            break
        
        # Ejecutar el grafo
        # Inicializamos con campos vacíos para evitar errores de clave
        resultado = grafo.invoke({"mensaje": mensaje, "sentimiento": "", "historia": []})
        print("\nResultado Final:", resultado.get("mensaje"))
        print("Sentimiento:", resultado.get("sentimiento"))

if __name__ == "__main__":
    main()