import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parámetros del problema
profesores = ["Profe A", "Profe B", "Profe C"]
cursos = ["Matemáticas", "Historia", "Ciencia"]
salones = ["Aula 1", "Aula 2", "Aula 3"]
tiempos = ["Lun AM", "Lun PM", "Mar AM", "Mar PM", "Mié AM"]

# Crear una solución inicial aleatoria (horario)
def crear_horario():
    horario = []
    for tiempo in tiempos:
        for salon in salones:
            curso = random.choice(cursos)
            profe = random.choice(profesores)
            horario.append((tiempo, salon, curso, profe))
    return horario

# Contar conflictos
def contar_conflictos(horario):
    conflictos = 0
    tabla = {}
    for entrada in horario:
        tiempo, salon, curso, profe = entrada
        if tiempo not in tabla:
            tabla[tiempo] = {"profesores": set(), "salones": set()}
        if profe in tabla[tiempo]["profesores"]:
            conflictos += 1
        else:
            tabla[tiempo]["profesores"].add(profe)
        if salon in tabla[tiempo]["salones"]:
            conflictos += 1
        else:
            tabla[tiempo]["salones"].add(salon)
    return conflictos

# Intercambiar clases
def intercambiar(horario):
    nuevo = horario[:]
    i, j = random.sample(range(len(nuevo)), 2)
    nuevo[i], nuevo[j] = nuevo[j], nuevo[i]
    return nuevo

# Búsqueda tabú
def busqueda_tabu(iteraciones=100, tabu_tam=10):
    actual = crear_horario()
    graficar_horario(actual)

    df = pd.DataFrame(actual, columns=["Tiempo", "Salón", "Curso", "Profesor"])
    df = df.sort_values(by=["Tiempo", "Salón"]).reset_index(drop=True)
    print("\nHorario óptimo local:")
    print(df)
    
    mejor = actual
    mejor_conf = contar_conflictos(mejor)
    lista_tabu = []
    historial = []

    for _ in range(iteraciones):
        vecino = intercambiar(actual)
        if vecino in lista_tabu:
            continue
        conf = contar_conflictos(vecino)
        if conf < mejor_conf:
            mejor = vecino
            mejor_conf = conf
        actual = vecino
        lista_tabu.append(vecino)
        if len(lista_tabu) > tabu_tam:
            lista_tabu.pop(0)
        historial.append(mejor_conf)

    return mejor, mejor_conf, historial

# Graficar evolución de conflictos
def graficar_historial(historial):
    plt.figure(figsize=(8, 4))
    plt.plot(historial, marker='o', linestyle='-', color='blue')
    plt.title("Reducción de conflictos por iteración")
    plt.xlabel("Iteración")
    plt.ylabel("Conflictos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Graficar el horario óptimo local
def graficar_horario(horario):
    df = pd.DataFrame(horario, columns=["Tiempo", "Salón", "Curso", "Profesor"])
    df = df.sort_values(by=["Tiempo", "Salón"]).reset_index(drop=True)
    
    tiempo_indices = {t: i for i, t in enumerate(tiempos)}
    salon_indices = {s: i for i, s in enumerate(salones)}

    fig, ax = plt.subplots(figsize=(10, 5))

    colores = {
        "Matemáticas": "#FF9999",
        "Historia": "#99CCFF",
        "Ciencia": "#99FF99"
    }

    for _, row in df.iterrows():
        t = tiempo_indices[row["Tiempo"]]
        s = salon_indices[row["Salón"]]
        curso = row["Curso"]
        profe = row["Profesor"]
        ax.barh(s, 0.8, left=t, color=colores.get(curso, "gray"), edgecolor="black")
        ax.text(t + 0.1, s, f"{curso}\n{profe}", va="center", ha="left", fontsize=8)

    ax.set_yticks(list(salon_indices.values()))
    ax.set_yticklabels(salones)
    ax.set_xticks(range(len(tiempos)))
    ax.set_xticklabels(tiempos, rotation=45)
    ax.set_xlabel("Tiempo")
    ax.set_title("Horario óptimo local (por salón y tiempo)")
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

# Ejecutar
mejor_horario, conflictos, historial = busqueda_tabu()

print("Conflictos encontrados en el mejor horario:", conflictos)
df = pd.DataFrame(mejor_horario, columns=["Tiempo", "Salón", "Curso", "Profesor"])
df = df.sort_values(by=["Tiempo", "Salón"]).reset_index(drop=True)
print("\nHorario óptimo local:")
print(df)

# Mostrar gráficas
graficar_historial(historial)
graficar_horario(mejor_horario)
