# Análisis de Impacto de Recursos - Proyecto Cronograma

## Resumen Ejecutivo

El análisis compara dos escenarios del proyecto:
- **Fase 1 (Línea Base)**: Sin restricciones de recursos
- **Fase 2 (Con Requisitos)**: Con restricciones de disponibilidad de recursos

### Hallazgos Principales

**Impacto en Duración Total del Proyecto:**
- Duración SIN requisitos: **13 semanas**
- Duración CON requisitos: **17 semanas**
- **Impacto total: +4 semanas** (30.8% de incremento)

## Cambios en el Camino Crítico

### Camino Crítico SIN Requisitos (13 semanas)
```
B → D → E → F → G → I → J → K → N → M
```
Tareas críticas: B, D, E, F, G, I, J, K, N, M (10 tareas)

### Camino Crítico CON Requisitos (17 semanas)
```
C (Documentación técnica)
```
Tareas críticas: C (1 tarea)

**Cambio crítico:** La Documentación Técnica (C) se convierte en la tarea crítica del proyecto debido a su restricción de "Dataset Limpio" que no está disponible hasta la semana 5.

## Análisis Detallado de Restricciones de Recursos

### Recursos Disponibles
1. **Servidor GPU**: Disponible desde semana 6
2. **Responsable Web**: Disponible desde semana 4
3. **Dataset Limpio**: Disponible desde semana 5

### Impacto por Tarea

#### Tareas con Mayor Impacto

| Tarea | Nombre | Requisito | Impacto_TC | Impacto_H | Observación |
|-------|--------|-----------|-----------|-----------|------------|
| **C** | Documentación técnica | Dataset Limpio | +5 sem | -1 sem | CRÍTICA ahora |
| **L** | Desarrollar UI/UX Web | Responsable Web | +3 sem | +1 sem | Retrasada 3 semanas |
| **I** | Entrenar Modelo | Servidor GPU | +1 sem | +3 sem | Retrasada 1 semana |
| **J** | Validación cruzada | Servidor GPU | +1 sem | +3 sem | Retrasada 1 semana |
| **K** | Clasificadora CLI | - | +1 sem | +3 sem | Efecto cascada |
| **M** | Despliegue web | - | +1 sem | +3 sem | Efecto cascada |
| **N** | Integrar IA en la Web | - | +1 sem | +3 sem | Efecto cascada |

#### Tareas sin Impacto
- **A**: Detectar Stakeholders (sin requisitos)
- **B**: Identificar infraestructuras (sin requisitos)
- **D**: Buscar Dataset secundario (sin requisitos)
- **E**: Explorar Dataset (sin requisitos)
- **F**: Unificar datasets (sin requisitos)
- **G**: Definir batches (sin requisitos)
- **H**: Definir Cronograma (sin requisitos)

## Recomendaciones Estratégicas

### 1. Prioritizar la Adquisición del Dataset Limpio
- **Acción**: Adelantar la disponibilidad del Dataset Limpio lo máximo posible
- **Impacto**: Cada semana que se adelante reduce el proyecto en 1 semana
- **Justificación**: Es el cuello de botella principal (bloquea la documentación técnica durante 5 semanas)

### 2. Asegurar la Disponibilidad del Responsable Web
- **Acción**: Confirmar disponibilidad desde la semana 1-2 (en lugar de semana 4)
- **Impacto**: Adelantaría L de semana 4 a semana 1
- **Justificación**: L actualmente tiene 7 semanas de holgura

### 3. Preasignar el Servidor GPU
- **Acción**: Reservar el servidor GPU desde la semana 4-5 (en lugar de semana 6)
- **Impacto**: Adelantaría I y J en 1 semana
- **Justificación**: Afecta la cadena crítica de ML

### 4. Paralelizar cuando sea posible
- La Documentación (C) puede ejecutarse en paralelo con otras tareas
- Considerar dividir C en fases tempranas (que no requieren Dataset Limpio) y fases tardías

## Archivos Generados

### Diagramas Fase 1 (Sin Requisitos) - `images-no-requirements/`
- `cronograma_pert.png`: Diagrama PERT con línea base
- `gantt_izquierda.html`: Gantt con inicio temprano
- `gantt_centrado.html`: Gantt equilibrado
- `gantt_derecha.html`: Gantt con inicio tardío

### Diagramas Fase 2 (Con Requisitos) - `images-with-requirements/`
- `cronograma_pert.png`: Diagrama PERT con restricciones
- `gantt_izquierda.html`: Gantt con inicio temprano
- `gantt_centrado.html`: Gantt equilibrado
- `gantt_derecha.html`: Gantt con inicio tardío

### Análisis Comparativo
- `impacto_recursos.csv`: Tabla comparativa con métricas de impacto

## Conclusiones

1. **Los recursos son un factor crítico**: Incrementan la duración del proyecto en 4 semanas (30.8%)

2. **Cambio radical del camino crítico**: De una cadena de 10 tareas a una única tarea crítica (Documentación)

3. **El Dataset Limpio es el cuello de botella**: Su disponibilidad determina la duración del proyecto

4. **Hay oportunidades de optimización**: Con una mejor gestión de recursos, se podrían recuperar hasta 4 semanas

5. **Las tareas de ML sufren menos**: I y J solo se retrasan 1 semana por el Servidor GPU

---

*Análisis generado por: Sistema PERT/Gantt con Análisis de Recursos*
*Fecha: 18 de febrero de 2026*
