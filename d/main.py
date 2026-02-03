from utils import Estado, invoke_llm
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

def nodo_1(estado: Estado) -> Estado:
    respuesta = invoke_llm("llama3.2", "Responde a este mensaje en español: " + estado["mensaje"], streaming=True, print_label="nodo_1: ")
    return {"mensaje": respuesta}

def nodo_2(estado: Estado) -> Estado:
    respuesta = invoke_llm("llama3.2", "Resume este texto en español: " + estado["mensaje"], streaming=True, print_label="nodo_2: ")
    return {"mensaje": respuesta}

def nodo_3(estado: Estado) -> Estado:
    respuesta = invoke_llm("llama3.2", "Analiza el sentimiento de este texto en español (positivo, negativo, neutral): " + estado["mensaje"], streaming=True, print_label="nodo_3: ")
    return {"mensaje": estado["mensaje"], "sentimiento": respuesta}

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
    constructor.add_edge("nodo_3", END)
    
    # Compilar el grafo
    grafo = constructor.compile()
    
    while True:
        mensaje = input(">>>  ")
        if mensaje.lower() == "salir":
            break
        # Ejecutar el grafo
        resultado = grafo.invoke({"mensaje": mensaje, "sentimiento": ""})
        print("Resultado:", resultado["mensaje"], "Sentimiento:", resultado["sentimiento"])

if __name__ == "__main__":
    main()
