import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import os

# Crear carpeta de imágenes si no existe
if not os.path.exists('images'):
    os.makedirs('images')

# tasks = {
#     "A": {"nombre": "Detectar Stakeholders", "duracion": 1, "dependencias": []},
#     "B": {"nombre": "Identificar infraestructuras", "duracion": 1, "dependencias": []},
#     "C": {"nombre": "Documentación técnica", "duracion": 12, "dependencias": []},
#     "D": {"nombre": "Buscar Dataset secundario", "duracion": 1, "dependencias": ["B"]},
#     "E": {"nombre": "Explorar Dataset", "duracion": 1, "dependencias": ["D", "B"]},
#     "F": {"nombre": "Unificar datasets", "duracion": 1, "dependencias": ["E"]},
#     "G": {"nombre": "Definir batches", "duracion": 1, "dependencias": ["F"]},
#     "H": {"nombre": "Definir Cronograma (PERT/Gantt)", "duracion": 1, "dependencias": ["A", "B"]},
#     "I": {"nombre": "Entrenar Modelo", "duracion": 2, "dependencias": ["G", "H"]},
#     "J": {"nombre": "Validación cruzada", "duracion": 1, "dependencias": ["I"]},
#     "K": {"nombre": "Clasificadora CLI", "duracion": 2, "dependencias": ["J"]},
#     "L": {"nombre": "Desarrollar UI/UX Web", "duracion": 3, "dependencias": ["A"]},
#     "N": {"nombre": "Integrar IA en la Web", "duracion": 2, "dependencias": ["K", "L"]},
#     "M": {"nombre": "Despliegue web", "duracion": 1, "dependencias": ["N"]}
# }

tasks = {
    "A": {"nombre": "Detectar Stakeholders", "duracion": 1, "dependencias": []},
    "B": {"nombre": "Identificar infraestructuras", "duracion": 1, "dependencias": []},
    "C": {"nombre": "Documentación técnica", "duracion": 8, "dependencias": []},
    "D": {"nombre": "Buscar Dataset secundario", "duracion": 1, "dependencias": []},
    "E": {"nombre": "Explorar Dataset", "duracion": 1, "dependencias": ["D"]},
    "F": {"nombre": "Unificar datasets", "duracion": 1, "dependencias": ["E"]},
    "G": {"nombre": "Definir batches", "duracion": 1, "dependencias": ["F"]},
    "H": {"nombre": "Definir Cronograma (PERT/Gantt)", "duracion": 1, "dependencias": [ "B"]},
    "I": {"nombre": "Entrenar Modelo", "duracion": 2, "dependencias": ["G", "H"]},
    "J": {"nombre": "Validación cruzada", "duracion": 1, "dependencias": ["I"]},
    "K": {"nombre": "Clasificadora CLI", "duracion": 2, "dependencias": ["J"]},
    "L": {"nombre": "Desarrollar UI/UX Web", "duracion": 0.5, "dependencias": []},
    "N": {"nombre": "Integrar IA en la Web", "duracion": 1, "dependencias": ["K", "L"]},
    "M": {"nombre": "Despliegue web", "duracion": 1, "dependencias": ["N"]}
}

def calcular_tiempos(task_id):
    # Si ya se calculó antes, no hacemos nada (evita repetir trabajo)
    if "TC" in tasks[task_id]:
        return tasks[task_id]["TC"]

    deps = tasks[task_id]["dependencias"]
    print(f"Calculando tiempos para {task_id}: dependencias = {deps}")
    
    if not deps:
        tasks[task_id]["IC"] = 0
    else:
        # RECURSIÓN: Asegura que cada dependencia esté calculada antes de seguir
        for d in deps:
            calcular_tiempos(d)
        tasks[task_id]["IC"] = max(tasks[d]["TC"] for d in deps)

    tasks[task_id]["TC"] = tasks[task_id]["IC"] + tasks[task_id]["duracion"]
    print(f"  {task_id}: IC={tasks[task_id]['IC']}, TC={tasks[task_id]['TC']}")
    return tasks[task_id]["TC"]

# Ejecutamos la función para todas las tareas
print("=== CALCULANDO TIEMPOS TEMPRANOS ===")
for t in tasks:
    calcular_tiempos(t)

print("\n=== TAREAS DESPUÉS DE CALCULAR TIEMPOS ===")
print(tasks)

duracion_proyecto = max(tasks[task]["TC"] for task in tasks)
print(f"\nLa duración total del proyecto es de {duracion_proyecto} semanas")


# Calcular Términos Lejanos y Inicios Lejanos. TL IL

def calcular_lejanos(task_id):
    if "IL" in tasks[task_id]:
        return tasks[task_id]["IL"]

    # Encontrar tareas que dependen de la actual
    sucesores = [t for t, info in tasks.items() if task_id in info["dependencias"]]
    print(f"Calculando lejanos para {task_id}: sucesores = {sucesores}")

    if not sucesores:
        tasks[task_id]["TL"] = duracion_proyecto
    else:
        # RECURSIÓN: Asegura que cada sucesor esté calculado antes de seguir
        for s in sucesores:
            calcular_lejanos(s)
        tasks[task_id]["TL"] = min(tasks[s]["IL"] for s in sucesores)

    tasks[task_id]["IL"] = tasks[task_id]["TL"] - tasks[task_id]["duracion"]
    print(f"  {task_id}: IL={tasks[task_id]['IL']}, TL={tasks[task_id]['TL']}")
    return tasks[task_id]["IL"]

# Ejecutamos la función para todas las tareas
print("\n=== CALCULANDO TIEMPOS LEJANOS ===")
for t in tasks:
    calcular_lejanos(t)

# Calcular Holgura
for t in tasks:
    tasks[t]["H"] = tasks[t]["IL"] - tasks[t]["IC"]

# camino crítico

camino_critico = [task for task in tasks if tasks[task]["H"] == 0]


dataFrame_Proyecto = pd.DataFrame({
    "Tarea": [tasks[task]["nombre"] for task in tasks],
    "Duración": [tasks[task]["duracion"] for task in tasks],
    "IC": [tasks[task]["IC"] for task in tasks],
    "TC": [tasks[task]["TC"] for task in tasks],
    "IL": [tasks[task]["IL"] for task in tasks],
    "TL": [tasks[task]["TL"] for task in tasks],
    "H": [tasks[task]["H"] for task in tasks]
}, index=list(tasks.keys()))

print(dataFrame_Proyecto)


dataFrame_Proyecto = pd.DataFrame.from_dict(tasks,columns=["nombre","duracion","IC","TC","IL","TL","H"],orient = "index")

print(dataFrame_Proyecto)

# Creamos nuestro objeto Grafo
print("\n=== CREANDO GRAFO PERT ===")
Grafo = nx.DiGraph()

# Añadimos un nodo al Grafo por cada tarea en el proyecto
for task in tasks:
    Grafo.add_node(task)

# A continuación añadimos las dependencias: para ello, miramos en cada tarea cuales son sus dependencias, y en el caso de haberlas, añadimos
# al grafo una dependencia entre ambas
for task in tasks:
    for dependencia in tasks[task]["dependencias"]:
        print(f"Añadiendo arista: {dependencia} -> {task}")
        Grafo.add_edge(dependencia, task)

print(f"Nodos en el grafo: {list(Grafo.nodes())}")
print(f"Aristas en el grafo: {list(Grafo.edges())}")

# 1. Posicionamiento basado en el TIEMPO DE CONCLUSIÓN (TC)
print("\n=== POSICIONANDO NODOS ===")
pos = {}
conteo_y = {}

# Ordenamos las tareas por TC para una mejor distribución inicial
tareas_ordenadas = sorted(tasks.keys(), key=lambda t: tasks[t]['TC'])

for task in tareas_ordenadas:
    data = tasks[task]
    # El eje X es el TC (donde termina la tarea)
    # Esto empuja las tareas largas o tardías hacia la derecha
    x = data['TC'] 
    
    # Gestión de colisiones en el eje Y
    if x not in conteo_y:
        conteo_y[x] = 0
    else:
        conteo_y[x] += 1
    
    y = conteo_y[x] * 0.8  # Separación vertical
    pos[task] = (x, y)

print("\n=== DIBUJANDO DIAGRAMA PERT ===")
plt.figure(figsize=(16, 9))

# Dibujamos el camino crítico y normal
colores_nodos = ["salmon" if nodo in camino_critico else "lightblue" for nodo in Grafo.nodes()]
edge_colors = ["red" if (u in camino_critico and v in camino_critico) else "#BDBDBD" for u, v in Grafo.edges()]

# Dibujar las aristas con flechas más visibles Y LINEAS RECTAS
nx.draw_networkx_edges(Grafo, pos, edge_color=edge_colors, width=2, 
                       arrowstyle='-|>', arrowsize=20, connectionstyle="arc3,rad=0")

# Dibujar nodos
nx.draw_networkx_nodes(Grafo, pos, node_color=colores_nodos, node_size=3000, 
                       edgecolors="white", linewidths=2)

# Etiquetas de los nodos (ID de la tarea)
nx.draw_networkx_labels(Grafo, pos, font_size=12, font_weight="bold")

# 2. Información detallada (Cuadros de tiempos)
for task, (x, y) in pos.items():
    d = tasks[task]
    # Formateamos la etiqueta con IC, TC, IL, TL y Holgura
    # Ponemos los valores de inicio a la izquierda y fin a la derecha para que sea intuitivo
    label_tiempos = (f"[{d['IC']}] --- ({d['TC']})\n"
                     f"[{d['IL']}] --- ({d['TL']})\n"
                     f"H: {d['H']}")
    
    plt.text(x, y + 0.05, label_tiempos, 
             bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray', boxstyle='round,pad=0.3'),
             fontsize=8, ha='center', va='bottom', family='monospace')

# Crear leyenda con nombres de tareas
legend_labels = [f"{task}: {tasks[task]['nombre']}" for task in sorted(tasks.keys())]
legend_text = "LEYENDA DE TAREAS\n" + "\n".join(legend_labels)

# Añadir leyenda como texto en la esquina superior derecha, fuera del gráfico
plt.text(1, 0.99, legend_text, 
         transform=plt.gca().transAxes,
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, pad=0.8),
         fontsize=9, verticalalignment='top', family='monospace')

# Ajustes de los ejes para que parezca una línea de tiempo real
plt.title("Cronograma PERT: Alineación por Tiempo de Conclusión (TC)", fontsize=16, pad=20)
plt.xlabel("Semanas (Progreso del Proyecto)", fontsize=12, fontweight='bold')

# Forzamos que el eje X muestre las semanas
max_semanas = max([d['TC'] for d in tasks.values()])
plt.xticks(range(0, max_semanas + 2)) 
plt.grid(True, axis='x', linestyle=':', alpha=0.6)

# Estética final
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.yticks([]) # Quitamos el eje Y porque es solo para separar nodos
plt.tight_layout()

# Guardar el diagrama en fichero
print("\nGuardando diagrama PERT...")
plt.savefig('images/cronograma_pert.png', dpi=300, bbox_inches='tight')
print("Diagrama PERT guardado en: images/cronograma_pert.png")
plt.close()



# Fijamos una fecha de inicio para nuestro proyecto
start_date = datetime(2026, 3, 1)

# Función para crear diagrama de Gantt con líneas de semanas
def crear_gantt(tareas_dict, titulo, filename):
    gantt_data = []
    
    for task in tareas_dict:
        gantt_data.append(dict(
            Tarea=tareas_dict[task]["nombre"],
            Inicio=start_date + timedelta(weeks=tareas_dict[task]["IC"]),
            Fin=start_date + timedelta(weeks=tareas_dict[task]["TC"]),
            Critica="Sí" if task in camino_critico else "No"
        ))
    
    gantt_df = pd.DataFrame(gantt_data)
    
    fig = px.timeline(
        gantt_df,
        x_start="Inicio",
        x_end="Fin",
        y="Tarea",
        color="Critica",
        title=titulo,
        color_discrete_map={"Sí": "#EF553B", "No": "#636EFA"}
    )
    
    fig.update_yaxes(autorange="reversed")
    
    # Añadir líneas verticales para cada semana sin anotaciones
    for week in range(duracion_proyecto + 1):
        week_date = start_date + timedelta(weeks=week)
        fig.add_vline(
            x=week_date,
            line_dash="dash",
            line_color="gray",
            opacity=0.3
        )
    
    fig.update_layout(
        hovermode="closest",
        height=600,
        xaxis_title="Semanas",
        yaxis_title="Tareas"
    )
    
    fig.write_html(filename)
    print(f"Diagrama guardado en: {filename}")
    return fig

# VERSIÓN 1: TODO A LA IZQUIERDA (máxima holgura aprovechada)
print("\n=== CREANDO DIAGRAMA GANTT IZQUIERDA ===")
gantt_izquierda = {}
for task in tasks:
    gantt_izquierda[task] = tasks[task].copy()
    gantt_izquierda[task]["IC"] = gantt_izquierda[task]["IC"]
    gantt_izquierda[task]["TC"] = gantt_izquierda[task]["IC"] + gantt_izquierda[task]["duracion"]

crear_gantt(gantt_izquierda, "Diagrama de Gantt - TODO A LA IZQUIERDA (Inicio temprano)", 
            "images/gantt_izquierda.html")

# VERSIÓN 2: CENTRADO (equilibrado)
print("\n=== CREANDO DIAGRAMA GANTT CENTRADO ===")
gantt_centrado = {}
for task in tasks:
    gantt_centrado[task] = tasks[task].copy()
    # Usar el punto medio entre IC e IL
    margen = (gantt_centrado[task]["IL"] - gantt_centrado[task]["IC"]) / 2
    gantt_centrado[task]["IC"] = gantt_centrado[task]["IC"] + margen
    gantt_centrado[task]["TC"] = gantt_centrado[task]["IC"] + gantt_centrado[task]["duracion"]

crear_gantt(gantt_centrado, "Diagrama de Gantt - CENTRADO (Equilibrio)", 
            "images/gantt_centrado.html")

# VERSIÓN 3: TODO A LA DERECHA (máxima holgura al final)
print("\n=== CREANDO DIAGRAMA GANTT DERECHA ===")
gantt_derecha = {}
for task in tasks:
    gantt_derecha[task] = tasks[task].copy()
    gantt_derecha[task]["TC"] = gantt_derecha[task]["TL"]
    gantt_derecha[task]["IC"] = gantt_derecha[task]["TC"] - gantt_derecha[task]["duracion"]

crear_gantt(gantt_derecha, "Diagrama de Gantt - TODO A LA DERECHA (Inicio tardío)", 
            "images/gantt_derecha.html")
