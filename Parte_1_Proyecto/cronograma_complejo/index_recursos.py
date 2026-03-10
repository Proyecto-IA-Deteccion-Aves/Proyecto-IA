import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import os
import copy

try:
    import kaleido
except ImportError:
    pass

# Crear carpetas de imágenes si no existen
if not os.path.exists('images-no-requirements'):
    os.makedirs('images-no-requirements')
if not os.path.exists('images-with-requirements'):
    os.makedirs('images-with-requirements')

# Diccionario de disponibilidad de recursos (semana en que están disponibles)
disponibilidad_recursos = {
    'Servidor': 5,
    'Responsable Web': 0,
    'Dataset': 3
}

tasks = {
    "A": {"nombre": "Detectar Stakeholders", "duracion": 1, "dependencias": [], "requisitos": []},
    "B": {"nombre": "Identificar infraestructuras", "duracion": 1, "dependencias": [], "requisitos": []},
    "C": {"nombre": "Documentación técnica", "duracion": 8, "dependencias": [], "requisitos": []},
    "D": {"nombre": "Buscar Dataset secundario", "duracion": 1, "dependencias": [], "requisitos": []},
    "E": {"nombre": "Explorar Dataset", "duracion": 1, "dependencias": ["D"], "requisitos": ["Dataset"]},
    "F": {"nombre": "Unificar datasets", "duracion": 1, "dependencias": ["E"], "requisitos": ["Dataset"]},
    "G": {"nombre": "Definir batches", "duracion": 1, "dependencias": ["F"], "requisitos": []},
    "H": {"nombre": "Definir Cronograma (PERT/Gantt)", "duracion": 1, "dependencias": [ "B"], "requisitos": []},
    "I": {"nombre": "Entrenar Modelo", "duracion": 2, "dependencias": ["G", "H"], "requisitos": ["Servidor", "Dataset"]},
    "J": {"nombre": "Validación cruzada", "duracion": 1, "dependencias": ["I"], "requisitos": ["Servidor", "Dataset"]},
    "K": {"nombre": "Clasificadora CLI", "duracion": 2, "dependencias": ["J"], "requisitos": []},
    "L": {"nombre": "Desarrollar UI/UX Web", "duracion": 0.5, "dependencias": [], "requisitos": ["Responsable Web"]},
    "N": {"nombre": "Integrar IA en la Web", "duracion": 1, "dependencias": ["K", "L"], "requisitos": ["Responsable Web"]},
    "M": {"nombre": "Despliegue web", "duracion": 1, "dependencias": ["N"], "requisitos": ["Responsable Web"]}
}

def calcular_tiempos(task_id, tasks_dict, considerar_recursos=False):
    # Si ya se calculó antes, no hacemos nada (evita repetir trabajo)
    if "TC" in tasks_dict[task_id]:
        return tasks_dict[task_id]["TC"]

    deps = tasks_dict[task_id]["dependencias"]
    print(f"Calculando tiempos para {task_id}: dependencias = {deps}")
    
    if not deps:
        tasks_dict[task_id]["IC"] = 0
    else:
        # RECURSIÓN: Asegura que cada dependencia esté calculada antes de seguir
        for d in deps:
            calcular_tiempos(d, tasks_dict, considerar_recursos)
        tasks_dict[task_id]["IC"] = max(tasks_dict[d]["TC"] for d in deps)
    
    # Si consideramos recursos, el IC es el máximo entre dependencias y disponibilidad de recursos
    if considerar_recursos and "requisitos" in tasks_dict[task_id]:
        for req in tasks_dict[task_id]["requisitos"]:
            if req in disponibilidad_recursos:
                tasks_dict[task_id]["IC"] = max(tasks_dict[task_id]["IC"], disponibilidad_recursos[req])

    tasks_dict[task_id]["TC"] = tasks_dict[task_id]["IC"] + tasks_dict[task_id]["duracion"]
    print(f"  {task_id}: IC={tasks_dict[task_id]['IC']}, TC={tasks_dict[task_id]['TC']}")
    return tasks_dict[task_id]["TC"]

def calcular_lejanos(task_id, tasks_dict, duracion_proyecto):
    if "IL" in tasks_dict[task_id]:
        return tasks_dict[task_id]["IL"]

    # Encontrar tareas que dependen de la actual
    sucesores = [t for t, info in tasks_dict.items() if task_id in info["dependencias"]]
    print(f"Calculando lejanos para {task_id}: sucesores = {sucesores}")

    if not sucesores:
        # Si no tiene sucesores, debe terminar en la semana final del proyecto
        tasks_dict[task_id]["TL"] = duracion_proyecto
    else:
        # RECURSIÓN: Asegura que cada sucesor esté calculado antes de seguir
        for s in sucesores:
            calcular_lejanos(s, tasks_dict, duracion_proyecto)
        # TL es el mínimo IC de sucesores (no IL)
        # La predecesora debe terminar cuando el sucesor comienza (IC), sin considerar holgura del sucesor
        tasks_dict[task_id]["TL"] = min(tasks_dict[s]["IC"] for s in sucesores)

    tasks_dict[task_id]["IL"] = tasks_dict[task_id]["TL"] - tasks_dict[task_id]["duracion"]
    print(f"  {task_id}: IL={tasks_dict[task_id]['IL']}, TL={tasks_dict[task_id]['TL']}")
    return tasks_dict[task_id]["IL"]

def procesar_proyecto(tasks_dict, considerar_recursos, carpeta_salida):
    """Procesa el proyecto calculando tiempos y generando diagramas"""
    # Crear una copia profunda para no modificar el original
    tasks_copy = copy.deepcopy(tasks_dict)
    
    print(f"\n{'='*60}")
    print(f"PROCESANDO PROYECTO - RECURSOS: {considerar_recursos}")
    print(f"{'='*60}\n")
    
    # Calculamos tiempos tempranos
    print("=== CALCULANDO TIEMPOS TEMPRANOS ===")
    for t in tasks_copy:
        calcular_tiempos(t, tasks_copy, considerar_recursos)

    print("\n=== TAREAS DESPUÉS DE CALCULAR TIEMPOS ===")
    print(tasks_copy)

    duracion_proyecto = max(tasks_copy[task]["TC"] for task in tasks_copy)
    print(f"\nLa duración total del proyecto es de {duracion_proyecto} semanas")

    # Calculamos tiempos lejanos
    print("\n=== CALCULANDO TIEMPOS LEJANOS ===")
    for t in tasks_copy:
        calcular_lejanos(t, tasks_copy, duracion_proyecto)

    # Calcular Holgura
    for t in tasks_copy:
        tasks_copy[t]["H"] = tasks_copy[t]["IL"] - tasks_copy[t]["IC"]

    # Camino crítico: encontrar rutas continuas desde inicio hasta fin sin gaps
    def encontrar_camino_critico(tasks_dict, duracion_total):
        """Encuentra el camino crítico: tareas que forman rutas continuas desde inicio a fin sin gaps"""
        camino_critico_set = set()
        
        # Encontrar tareas finales (que terminan en la duración total del proyecto)
        tareas_finales = [t for t in tasks_dict if tasks_dict[t]["TC"] == duracion_total]
        
        def rastrear_hacia_atras(task_id):
            """Rastrear recursivamente desde una tarea hacia sus predecesoras críticas"""
            if task_id in camino_critico_set:
                return
            
            camino_critico_set.add(task_id)
            deps = tasks_dict[task_id]["dependencias"]
            
            if not deps:
                # Tarea sin dependencias que es final - es crítica
                return
            
            # Una predecesora es crítica si no hay gap entre su TC y nuestro IC
            # Es decir, si task.IC == predecesora.TC exactamente
            for dep in deps:
                if tasks_dict[dep]["TC"] == tasks_dict[task_id]["IC"]:
                    # No hay gap: esta predecesora es crítica
                    rastrear_hacia_atras(dep)
        
        # Comenzar desde tareas finales
        for tarea_final in tareas_finales:
            rastrear_hacia_atras(tarea_final)
        
        return sorted(list(camino_critico_set))
    
    camino_critico = encontrar_camino_critico(tasks_copy, duracion_proyecto)
    print(f"\n=== CAMINO CRÍTICO ===")
    print(f"Tareas críticas: {camino_critico}")
    print(f"Duración del camino crítico: {duracion_proyecto} semanas")

    # Crear DataFrame
    dataFrame_Proyecto = pd.DataFrame.from_dict(tasks_copy, columns=["nombre","duracion","IC","TC","IL","TL","H"], orient="index")
    print(f"\n{dataFrame_Proyecto}")

    return tasks_copy, camino_critico, duracion_proyecto, dataFrame_Proyecto

# FASE 1: Sin requisitos
print("\n" + "="*80)
print("FASE 1: LÍNEA BASE (SIN REQUISITOS)")
print("="*80)
tasks_sin_req = copy.deepcopy(tasks)

tasks_sin_req_resultado, critico_sin_req, duracion_sin_req, df_sin_req = procesar_proyecto(tasks_sin_req, False, 'images-no-requirements')

# FASE 2: Con requisitos
print("\n" + "="*80)
print("FASE 2: ANÁLISIS CON REQUISITOS")
print("="*80)
tasks_con_req = copy.deepcopy(tasks)

tasks_con_req_resultado, critico_con_req, duracion_con_req, df_con_req = procesar_proyecto(tasks_con_req, True, 'images-with-requirements')

# FASE 3: Generar diagramas para ambas versiones
def generar_diagramas(tasks_dict, camino_critico, duracion_proyecto, carpeta_salida, titulo_base, considerar_recursos):
    """Genera diagrama PERT y 3 diagramas Gantt"""
    
    # Creamos nuestro objeto Grafo
    print(f"\n=== CREANDO GRAFO PERT para {carpeta_salida} ===")
    Grafo = nx.DiGraph()

    # Añadimos un nodo al Grafo por cada tarea en el proyecto
    for task in tasks_dict:
        Grafo.add_node(task)

    # A continuación añadimos las dependencias
    for task in tasks_dict:
        for dependencia in tasks_dict[task]["dependencias"]:
            Grafo.add_edge(dependencia, task)

    # 1. Posicionamiento basado en el TÉRMINO LEJANO (TL) - Máxima posición a la derecha
    pos = {}
    conteo_y = {}

    # Ordenamos las tareas por TL para una mejor distribución inicial
    tareas_ordenadas = sorted(tasks_dict.keys(), key=lambda t: tasks_dict[t]['TL'])

    for task in tareas_ordenadas:
        data = tasks_dict[task]
        x = data['TL']
        
        # Gestión de colisiones en el eje Y
        if x not in conteo_y:
            conteo_y[x] = 0
        else:
            conteo_y[x] += 1
        
        y = conteo_y[x] * 0.8  # Separación vertical aumentada
        pos[task] = (x, y)

    # Dibujar PERT
    plt.figure(figsize=(18, 12))

    # Mapa de colores para requisitos
    colores_requisitos = {
        'Servidor': '#FF6B6B',      # Rojo
        'Dataset': '#4ECDC4',    # Turquesa
        'Responsable Web': '#FFE66D'    # Amarillo
    }

    # Obtener el rango de semanas
    max_semanas = max([d['TL'] for d in tasks_dict.values()])
    min_semanas = 0
    
    if considerar_recursos:
        # Dibujar líneas discontinuas de disponibilidad de requisitos en la parte superior
        ax = plt.gca()
        disponibilidad_y_offset = max([pos[t][1] for t in pos]) + 1.5
        
        requisitos_unicos = set()
        for task in tasks_dict:
            requisitos_unicos.update(tasks_dict[task].get('requisitos', []))
        
        requisitos_ordenados = sorted(list(requisitos_unicos))
        for idx, requisito in enumerate(requisitos_ordenados):
            disponibilidad_semana = disponibilidad_recursos.get(requisito, 0)
            color = colores_requisitos.get(requisito, 'gray')
            y_pos = disponibilidad_y_offset + (idx * 0.6)
            
            # Dibujar línea discontinua desde la semana de disponibilidad hasta el final
            ax.plot([disponibilidad_semana, max_semanas], [y_pos, y_pos], 
                    linestyle='--', linewidth=2.5, color=color, alpha=0.7)
            
            # Añadir etiqueta del requisito
            ax.text(disponibilidad_semana - 0.3, y_pos, requisito, 
                    fontsize=9, fontweight='bold', ha='right', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3, edgecolor=color))

    # Dibujamos el camino crítico y normal
    colores_nodos = ["salmon" if nodo in camino_critico else "lightblue" for nodo in Grafo.nodes()]
    edge_colors = ["red" if (u in camino_critico and v in camino_critico) else "#BDBDBD" for u, v in Grafo.edges()]

    # Dibujar las aristas con flechas más visibles Y LINEAS RECTAS
    nx.draw_networkx_edges(Grafo, pos, edge_color=edge_colors, width=2, 
                           arrowstyle='-|>', arrowsize=20, connectionstyle="arc3,rad=0")

    # Dibujar nodos con bordes coloreados según requisitos
    nodos_lista = list(Grafo.nodes())
    for idx, nodo in enumerate(nodos_lista):
        requisitos = tasks_dict[nodo].get('requisitos', [])
        
        if requisitos:
            # Si tiene requisitos, usar el color del primer requisito como borde principal
            color_borde = colores_requisitos.get(requisitos[0], 'gray')
            # Si tiene múltiples requisitos, usar un borde más grueso
            ancho_borde = 3.5 if len(requisitos) > 1 else 2.5
        else:
            # Sin requisitos, borde gris
            color_borde = 'gray'
            ancho_borde = 2
        
        nx.draw_networkx_nodes(Grafo, pos, nodelist=[nodo], node_color=[colores_nodos[idx]], 
                               node_size=2000, edgecolors=color_borde, linewidths=ancho_borde)

    # Etiquetas de los nodos (ID de la tarea)
    nx.draw_networkx_labels(Grafo, pos, font_size=10, font_weight="bold")

    # 2. Información detallada (Cuadros de tiempos)
    for task, (x, y) in pos.items():
        d = tasks_dict[task]
        label_tiempos = (f"[{d['IC']}] --- ({d['TC']})\n"
                         f"[{d['IL']}] --- ({d['TL']})\n"
                         f"H: {d['H']}")
        
        plt.text(x, y + 0.15, label_tiempos, 
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray', boxstyle='round,pad=0.3'),
                 fontsize=7, ha='center', va='bottom', family='monospace')

    # Crear leyenda con nombres de tareas Y REQUISITOS
    legend_labels = []
    for task in sorted(tasks_dict.keys()):
        nombre = tasks_dict[task]['nombre']
        requisitos = tasks_dict[task].get('requisitos', [])
        if requisitos:
            req_str = f" [Req: {', '.join(requisitos)}]"
        else:
            req_str = ""
        legend_labels.append(f"{task}: {nombre}{req_str}")
    
    # Agregar leyenda de colores de requisitos
    legend_colors = "\n\n═ COLORES DE BORDE (Requisitos) ═\n"
    legend_colors += "Rojo: Servidor\n"
    legend_colors += "Turquesa: Dataset\n"
    legend_colors += "Amarillo: Responsable Web\n"
    legend_colors += "Gris: Sin requisitos\n"
    legend_colors += "═══ Borde grueso = múltiples requisitos"
    
    legend_text = "LEYENDA DE TAREAS\n" + "\n".join(legend_labels) + legend_colors

    # Añadir leyenda como texto en la esquina superior derecha, fuera del gráfico
    plt.text(1.02, 0.99, legend_text, 
             transform=plt.gca().transAxes,
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.95, pad=0.8, edgecolor='gray', linewidth=2),
             fontsize=7.5, verticalalignment='top', family='monospace')

    # Ajustes de los ejes para que parezca una línea de tiempo real
    plt.title(f"{titulo_base}: Alineación por Término Lejano (TL) - Máximo desplazamiento a la derecha", fontsize=16, pad=50)
    plt.xlabel("Semanas (Término Lejano - TL)", fontsize=12, fontweight='bold')

    # Forzamos que el eje X muestre las semanas
    max_semanas = max([d['TL'] for d in tasks_dict.values()])
    plt.xticks(range(0, max_semanas + 2)) 
    plt.grid(True, axis='x', linestyle=':', alpha=0.6)

    # Estética final
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.yticks([]) # Quitamos el eje Y porque es solo para separar nodos
    plt.tight_layout()

    # Guardar el diagrama en fichero
    print(f"\nGuardando diagrama PERT...")
    plt.savefig(f'{carpeta_salida}/cronograma_pert.png', dpi=300, bbox_inches='tight')
    print(f"Diagrama PERT guardado en: {carpeta_salida}/cronograma_pert.png")
    plt.close()

    # Generar Gantt charts
    start_date = datetime(2026, 3, 1)
    
    def crear_gantt(tareas_dict, titulo, filename):
        gantt_data = []
        
        for task in tareas_dict:
            requisitos = tareas_dict[task].get('requisitos', [])
            req_text = f" [Requisitos: {', '.join(requisitos)}]" if requisitos else " [Sin requisitos]"
            tarea_label = f"{task}: {tareas_dict[task]['nombre']}{req_text}"
            
            gantt_data.append(dict(
                Tarea=tarea_label,
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
            height=700,
            xaxis_title="Semanas",
            yaxis_title="Tareas"
        )
        
        fig.write_html(filename)
        print(f"Diagrama guardado en: {filename}")
        
        # Guardar también como PNG
        png_filename = filename.replace('.html', '.png')
        try:
            fig.write_image(png_filename, width=1400, height=700)
            print(f"Imagen guardada en: {png_filename}")
        except Exception as e:
            print(f"Advertencia: No se pudo guardar la imagen PNG ({e})")
        
        return fig

    # VERSIÓN 1: TODO A LA IZQUIERDA (máxima holgura aprovechada)
    print(f"\n=== CREANDO DIAGRAMA GANTT IZQUIERDA en {carpeta_salida} ===")
    gantt_izquierda = {}
    for task in tasks_dict:
        gantt_izquierda[task] = tasks_dict[task].copy()
        gantt_izquierda[task]["IC"] = gantt_izquierda[task]["IC"]
        gantt_izquierda[task]["TC"] = gantt_izquierda[task]["IC"] + gantt_izquierda[task]["duracion"]

    crear_gantt(gantt_izquierda, f"{titulo_base} - TODO A LA IZQUIERDA (Inicio temprano)", 
                f"{carpeta_salida}/gantt_izquierda.html")

    # VERSIÓN 2: CENTRADO (equilibrado)
    print(f"\n=== CREANDO DIAGRAMA GANTT CENTRADO en {carpeta_salida} ===")
    gantt_centrado = {}
    
    # Procesar en orden topológico para garantizar que las dependencias sean respetadas
    orden_topologico = list(nx.topological_sort(Grafo))
    
    for task in orden_topologico:
        gantt_centrado[task] = tasks_dict[task].copy()
        # Usar el punto medio entre IC e IL
        margen = (gantt_centrado[task]["IL"] - gantt_centrado[task]["IC"]) / 2
        ic_centrado = gantt_centrado[task]["IC"] + margen
        
        # Garantizar que el IC centrado respeta las dependencias
        deps = gantt_centrado[task]["dependencias"]
        if deps:
            ic_minimo_requerido = max(gantt_centrado[d]["TC"] for d in deps)
            ic_centrado = max(ic_centrado, ic_minimo_requerido)
        
        gantt_centrado[task]["IC"] = ic_centrado
        gantt_centrado[task]["TC"] = gantt_centrado[task]["IC"] + gantt_centrado[task]["duracion"]

    crear_gantt(gantt_centrado, f"{titulo_base} - CENTRADO (Equilibrio)", 
                f"{carpeta_salida}/gantt_centrado.html")

    # VERSIÓN 3: TODO A LA DERECHA (máxima holgura al final)
    print(f"\n=== CREANDO DIAGRAMA GANTT DERECHA en {carpeta_salida} ===")
    gantt_derecha = {}
    for task in tasks_dict:
        gantt_derecha[task] = tasks_dict[task].copy()
        gantt_derecha[task]["TC"] = gantt_derecha[task]["TL"]
        gantt_derecha[task]["IC"] = gantt_derecha[task]["TC"] - gantt_derecha[task]["duracion"]

    crear_gantt(gantt_derecha, f"{titulo_base} - TODO A LA DERECHA (Inicio tardío)", 
                f"{carpeta_salida}/gantt_derecha.html")

# Generar diagramas para ambas fases
print("\n" + "="*80)
print("GENERANDO DIAGRAMAS - FASE 1 (SIN REQUISITOS)")
print("="*80)
generar_diagramas(tasks_sin_req_resultado, critico_sin_req, duracion_sin_req, 'images-no-requirements', 'Cronograma PERT - SIN REQUISITOS', False)

print("\n" + "="*80)
print("GENERANDO DIAGRAMAS - FASE 2 (CON REQUISITOS)")
print("="*80)
generar_diagramas(tasks_con_req_resultado, critico_con_req, duracion_con_req, 'images-with-requirements', 'Cronograma PERT - CON REQUISITOS', True)

# FASE 3: Crear análisis comparativo
print("\n" + "="*80)
print("FASE 3: ANÁLISIS DE IMPACTO DE RECURSOS")
print("="*80)

# Crear DataFrame comparativo
impacto_data = []
for task_id in sorted(tasks.keys()):
    impacto_data.append({
        'Tarea': task_id,
        'Nombre': tasks[task_id]['nombre'],
        'Duración': tasks[task_id]['duracion'],
        'Requisitos': ', '.join(tasks[task_id].get('requisitos', [])) or 'Ninguno',
        'IC_Sin_Req': tasks_sin_req_resultado[task_id]['IC'],
        'TC_Sin_Req': tasks_sin_req_resultado[task_id]['TC'],
        'H_Sin_Req': tasks_sin_req_resultado[task_id]['H'],
        'IC_Con_Req': tasks_con_req_resultado[task_id]['IC'],
        'TC_Con_Req': tasks_con_req_resultado[task_id]['TC'],
        'H_Con_Req': tasks_con_req_resultado[task_id]['H'],
        'Impacto_TC': tasks_con_req_resultado[task_id]['TC'] - tasks_sin_req_resultado[task_id]['TC'],
        'Impacto_H': tasks_con_req_resultado[task_id]['H'] - tasks_sin_req_resultado[task_id]['H'],
        'Crítica_Sin_Req': 'Sí' if task_id in critico_sin_req else 'No',
        'Crítica_Con_Req': 'Sí' if task_id in critico_con_req else 'No'
    })

impacto_df = pd.DataFrame(impacto_data)
print(f"\n{impacto_df}")

print(f"\n{'='*80}")
print(f"RESUMEN DEL ANÁLISIS")
print(f"{'='*80}")
print(f"Duración SIN requisitos: {duracion_sin_req} semanas")
print(f"Duración CON requisitos: {duracion_con_req} semanas")
print(f"Impacto total: +{duracion_con_req - duracion_sin_req} semanas")
print(f"\nCamino crítico SIN requisitos: {critico_sin_req}")
print(f"Camino crítico CON requisitos: {critico_con_req}")
print(f"\nTareas que PIERDEN holgura por recursos:")
for task_id in sorted(tasks.keys()):
    h_sin = tasks_sin_req_resultado[task_id]['H']
    h_con = tasks_con_req_resultado[task_id]['H']
    if h_con < h_sin:
        print(f"  {task_id}: {h_sin} → {h_con} (pierde {h_sin - h_con} semanas de holgura)")

print(f"\n{'='*80}")
print(f"¡Análisis completado!")
print(f"{'='*80}")

