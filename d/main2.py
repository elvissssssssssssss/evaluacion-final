import uuid
from utils import create_graph_main2



def main():
    grafo = create_graph_main2()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        mensaje = input("Ingresa un mensaje (o 'salir' para terminar): ")
        if mensaje.lower() == "salir":
            break

        estado = {"mensaje": mensaje, "sentimiento": "", "historia": []}

        resultado = grafo.invoke(estado, config)
        print("Resultado final:", resultado["mensaje"], "Sentimiento:", resultado["sentimiento"])

if __name__ == "__main__":
    main()