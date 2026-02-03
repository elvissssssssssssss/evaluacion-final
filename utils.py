import os
from typing import TypedDict
from langchain_ollama import OllamaLLM
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

_callback = None

def set_callback(callback):
    global _callback
    _callback = callback

class Estado(TypedDict):
    mensaje: str
    sentimiento: str
    historia: list[str]

def build_context(historia: list[str]) -> str:
    return "\n".join(historia) if historia else ""

def invoke_llm(model: str, prompt: str, streaming=False, print_label="") -> str:
    global _callback
    llm = OllamaLLM(model=model)
    respuesta = ""
    if streaming and print_label:
        if _callback:
            _callback(print_label)
        else:
            print(print_label, end="", flush=True)
    for chunk in llm.stream(prompt):
        if streaming:
            if _callback:
                _callback(chunk)
            else:
                print(chunk, end="", flush=True)
        respuesta += chunk
    if streaming and not _callback:
        print()
    return respuesta.strip()

def create_node(prompt_template: str, model: str, node_name: str, history_append_func, output_key: str = "mensaje", extra_updates_func=None):
    def node_func(estado: Estado) -> Estado:
        contexto = build_context(estado["historia"])
        prompt = prompt_template.format(contexto=contexto, mensaje=estado['mensaje'])
        result = invoke_llm(model, prompt, streaming=True, print_label=f"{node_name}: ")
        nueva_historia = estado["historia"] + history_append_func(estado, result)
        update = {output_key: result, "historia": nueva_historia}
        if extra_updates_func:
            update.update(extra_updates_func(estado, result))
        return update
    return node_func

def create_graph_main2():
    nodo_1 = create_node(
        "Contexto anterior:\n{contexto}\nResponde a este mensaje en español: {mensaje}",
        "gpt-oss:20b-cloud",
        "nodo_1",
        lambda estado, result: [f"Usuario: {estado['mensaje']}", f"Nodo_1: {result}"]
    )

    nodo_2 = create_node(
        "Contexto anterior:\n{contexto}\nResume este texto en español: {mensaje}",
        "gpt-oss:20b-cloud",
        "nodo_2",
        lambda estado, result: [f"Nodo_2: {result}"]
    )

    nodo_3 = create_node(
        "Contexto anterior:\n{contexto}\nAnaliza el sentimiento de este texto en español (positivo, negativo, neutral): {mensaje}",
        "gpt-oss:20b-cloud",
        "nodo_3",
        lambda estado, result: [f"Nodo_3: {result}"],
        output_key="sentimiento",
        extra_updates_func=lambda estado, result: {"mensaje": estado["mensaje"]}
    )

    constructor = StateGraph(Estado)
    constructor.add_node("nodo_1", nodo_1)
    constructor.add_node("nodo_2", nodo_2)
    constructor.add_node("nodo_3", nodo_3)
    constructor.add_edge(START, "nodo_1")
    constructor.add_edge("nodo_1", "nodo_2")
    constructor.add_edge("nodo_2", "nodo_3")
    constructor.add_edge("nodo_3", END)
    checkpointer = MemorySaver()
    grafo = constructor.compile(checkpointer=checkpointer)
    return grafo

def nodo_1_simple(estado: Estado) -> Estado:
    respuesta = invoke_llm("gpt-oss:20b-cloud", "Responde a este mensaje en español: " + estado["mensaje"], streaming=True)
    return {"mensaje": respuesta}

def nodo_2_simple(estado: Estado) -> Estado:
    respuesta = invoke_llm("gpt-oss:20b-cloud", "Resume este texto en español: " + estado["mensaje"], streaming=True)
    return {"mensaje": respuesta}

def nodo_3_simple(estado: Estado) -> Estado:
    respuesta = invoke_llm("gpt-oss:20b-cloud", "Analiza el sentimiento de este texto en español (positivo, negativo, neutral): " + estado["mensaje"], streaming=True)
    return {"mensaje": estado["mensaje"], "sentimiento": respuesta}

def create_graph_main():
    constructor = StateGraph(Estado)
    constructor.add_node("nodo_1", nodo_1_simple)
    constructor.add_node("nodo_2", nodo_2_simple)
    constructor.add_node("nodo_3", nodo_3_simple)
    constructor.add_edge(START, "nodo_1")
    constructor.add_edge("nodo_1", "nodo_2")
    constructor.add_edge("nodo_2", "nodo_3")
    constructor.add_edge("nodo_3", END)
    grafo = constructor.compile()
    return grafo