# 👥 Guía del Usuario - OkuoAgent

## 📋 Índice

1. [Primeros Pasos](#primeros-pasos)
2. [Interfaz de Usuario](#interfaz-de-usuario)
3. [Interacción con el Chat](#interacción-con-el-chat)
4. [Tipos de Consultas](#tipos-de-consultas)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [KPIs y Métricas](#kpis-y-métricas)
7. [Consejos y Mejores Prácticas](#consejos-y-mejores-prácticas)
8. [Solución de Problemas](#solución-de-problemas)

## 🚀 Primeros Pasos

### Acceso a la Aplicación

1. **Abrir el navegador** y dirigirse a: `http://localhost:8502`
2. **Esperar** a que la aplicación cargue completamente
3. **Verificar** que los datos estén disponibles (deberías ver KPIs en la pantalla)

### Verificación Inicial

Antes de empezar, asegúrate de que:

- ✅ **Los datos están cargados**: Verás métricas en la sección de KPIs
- ✅ **La conexión está activa**: No hay mensajes de error
- ✅ **El chat está disponible**: Puedes escribir en el campo de texto

## 🖥️ Interfaz de Usuario

### Pestañas Principales

#### 💬 Dashboard Inteligente
- **Propósito**: Chat principal con el agente de IA
- **Funcionalidades**:
  - Conversación natural con datos
  - Generación de gráficos automática
  - Análisis en tiempo real

#### 🔧 Depuración
- **Propósito**: Información técnica y debugging
- **Funcionalidades**:
  - Estado de sesiones
  - Información de memoria
  - Logs del sistema

### Elementos de la Interfaz

#### Panel de KPIs
```
┌─────────────────────────────────────┐
│ 📊 KPIs en Tiempo Real              │
├─────────────────────────────────────┤
│ Sackoff: 3.2%    │ Eficiencia: 94%  │
│ Durabilidad: 92% │ Dureza: 10.5     │
└─────────────────────────────────────┘
```

#### Chat Interface
```
┌─────────────────────────────────────┐
│ 💬 Chat con OkuoAgent               │
├─────────────────────────────────────┤
│ [Tu mensaje aquí...]                │
│                                    │
│ ┌─────────────────────────────────┐ │
│ │ Respuesta del agente            │ │
│ │ + Gráficos generados            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 💬 Interacción con el Chat

### Cómo Hacer una Consulta

1. **Escribe tu pregunta** en el campo de texto
2. **Presiona Enter** o haz clic en "Enviar"
3. **Espera** la respuesta del agente (5-10 segundos)
4. **Revisa** los resultados y gráficos generados

### Ejemplos de Consultas Efectivas

#### Consultas Básicas
```
"Muéstrame las tendencias de producción del último mes"
"¿Cuál es el sackoff promedio por planta?"
"Compara la calidad con y sin Adiflow"
```

#### Consultas Específicas
```
"Genera un gráfico de eficiencia por producto"
"Analiza las anomalías en dureza"
"Calcula los KPIs principales"
```

#### Consultas Avanzadas
```
"Identifica correlaciones entre presión y calidad"
"Predice tendencias de producción para el próximo trimestre"
"Detecta patrones estacionales en los datos"
```

## 📊 Tipos de Consultas

### 1. Análisis de Tendencias

#### Consultas de Tiempo
```
"¿Cómo ha evolucionado la producción en los últimos 3 meses?"
"Muéstrame las tendencias de calidad por semana"
"Analiza la estacionalidad de la producción"
```

#### Respuestas Esperadas
- Gráficos de líneas temporales
- Análisis de tendencias
- Identificación de patrones

### 2. Análisis Comparativo

#### Comparaciones por Categorías
```
"Compara la eficiencia entre plantas"
"¿Cuál es la diferencia de calidad con y sin Adiflow?"
"Analiza el rendimiento por producto"
```

#### Respuestas Esperadas
- Gráficos de barras comparativos
- Tablas de resumen
- Análisis estadístico

### 3. Detección de Anomalías

#### Identificación de Problemas
```
"Detecta valores atípicos en dureza"
"Identifica órdenes con bajo rendimiento"
"Encuentra anomalías en la producción"
```

#### Respuestas Esperadas
- Gráficos de dispersión
- Lista de anomalías
- Análisis de causas

### 4. Análisis de Correlaciones

#### Relaciones entre Variables
```
"¿Hay correlación entre presión y calidad?"
"Analiza la relación entre temperatura y eficiencia"
"Identifica factores que afectan el sackoff"
```

#### Respuestas Esperadas
- Matrices de correlación
- Gráficos de dispersión
- Análisis de regresión

## 📈 Interpretación de Resultados

### Gráficos Interactivos

#### Controles de Navegación
- **🔍 Zoom**: Haz clic y arrastra para hacer zoom
- **🖱️ Hover**: Pasa el mouse para ver detalles
- **📱 Pan**: Arrastra para mover la vista
- **🔄 Reset**: Doble clic para resetear la vista

#### Tipos de Gráficos

##### Gráficos de Líneas
```
┌─────────────────────────────────────┐
│ Tendencia de Producción             │
│                                     │
│    📈                               │
│   /                                 │
│  /                                  │
│ /                                   │
│/                                    │
└─────────────────────────────────────┘
```
**Uso**: Mostrar tendencias temporales

##### Gráficos de Barras
```
┌─────────────────────────────────────┐
│ Eficiencia por Planta               │
│                                     │
│ Planta A: ██████████ 95%            │
│ Planta B: ████████   80%            │
│ Planta C: ████████████ 100%         │
└─────────────────────────────────────┘
```
**Uso**: Comparar categorías

##### Gráficos de Dispersión
```
┌─────────────────────────────────────┐
│ Correlación: Presión vs Calidad     │
│                                     │
│   •  •  •                           │
│ •  •  •  •                          │
│   •  •  •                           │
└─────────────────────────────────────┘
```
**Uso**: Mostrar relaciones entre variables

### Tablas de Datos

#### Interpretación de Métricas
```
┌─────────────────────────────────────┐
│ Resumen Estadístico                 │
├─────────────────────────────────────┤
│ Métrica    │ Valor │ Unidad         │
├─────────────────────────────────────┤
│ Sackoff    │ 3.2%  │ Porcentaje     │
│ Eficiencia │ 94%   │ Porcentaje     │
│ Durabilidad│ 92%   │ Porcentaje     │
└─────────────────────────────────────┘
```

## 📊 KPIs y Métricas

### Métricas Principales

#### Sackoff
- **Definición**: Pérdida total por orden de producción
- **Cálculo**: `(toneladas_anuladas + diferencia_toneladas) / toneladas_a_producir`
- **Meta**: < 5%
- **Interpretación**: Menor es mejor

#### Eficiencia de Producción
- **Definición**: Porcentaje de producción vs. planificado
- **Cálculo**: `(toneladas_producidas / toneladas_a_producir) * 100`
- **Meta**: > 90%
- **Interpretación**: Mayor es mejor

#### Durabilidad QA
- **Definición**: Porcentaje de durabilidad oficial
- **Meta**: > 90%
- **Interpretación**: Mayor es mejor

#### Dureza QA
- **Definición**: Resistencia física del pellet (kg/cm²)
- **Meta**: 8-12 kg/cm²
- **Interpretación**: Dentro del rango es óptimo

### Filtros Especializados

#### Por Adiflow
```
# Datos con Adiflow
"Analiza la producción con Adiflow"

# Datos sin Adiflow
"Compara la calidad sin Adiflow"
```

#### Por Período
```
# Último mes
"Tendencias del último mes"

# Período específico
"Análisis de enero a marzo"
```

## 💡 Consejos y Mejores Prácticas

### Cómo Formular Consultas Efectivas

#### ✅ Consultas Bien Formuladas
```
"Muéstrame las tendencias de eficiencia por planta en el último trimestre"
"Compara la calidad QA entre productos con y sin Adiflow"
"Identifica las 5 órdenes con mayor sackoff"
```

#### ❌ Consultas a Evitar
```
"Analiza los datos" (muy vago)
"Todo" (demasiado amplio)
"¿Por qué?" (sin contexto específico)
```

### Estrategias de Análisis

#### 1. Empezar con lo General
```
"Muéstrame un resumen de los KPIs principales"
"¿Cuál es el estado general de la producción?"
```

#### 2. Profundizar en Áreas Específicas
```
"Analiza en detalle la planta con menor eficiencia"
"Investiga las causas del alto sackoff en julio"
```

#### 3. Comparar y Contrastar
```
"Compara el rendimiento entre turnos"
"Analiza las diferencias por producto"
```

#### 4. Buscar Patrones y Tendencias
```
"Identifica patrones estacionales"
"Detecta tendencias a largo plazo"
```

### Optimización de Consultas

#### Usar Lenguaje Específico
```
✅ "Calcula el sackoff promedio por planta"
❌ "Mira los números malos"
```

#### Especificar Períodos
```
✅ "Análisis de los últimos 30 días"
❌ "Recientemente"
```

#### Definir Métricas
```
✅ "Eficiencia de producción"
❌ "Rendimiento"
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### La aplicación no responde
**Síntomas**: 
- El chat no procesa consultas
- Gráficos no se cargan

**Soluciones**:
1. **Recargar la página** (F5)
2. **Verificar conexión** a internet
3. **Esperar** 30 segundos y reintentar
4. **Contactar** soporte técnico

#### Gráficos no se muestran
**Síntomas**:
- Respuesta de texto sin gráficos
- Errores en la consola

**Soluciones**:
1. **Verificar** que la consulta incluya análisis visual
2. **Reformular** la pregunta más específicamente
3. **Usar palabras clave** como "gráfico", "visualizar", "mostrar"

#### Errores de datos
**Síntomas**:
- Mensajes de error sobre variables
- Resultados inesperados

**Soluciones**:
1. **Verificar** que los datos estén cargados
2. **Usar nombres de columnas** correctos
3. **Consultar** la documentación de datos

### Mensajes de Error Comunes

#### "No se encontraron datos"
```
Solución: Verificar que la base de datos esté conectada
```

#### "Variable no definida"
```
Solución: Usar nombres de columnas exactos de la tabla
```

#### "Error de conexión"
```
Solución: Verificar configuración de red y base de datos
```

### Contacto de Soporte

#### Cuándo Contactar Soporte
- ✅ La aplicación no inicia
- ✅ Errores persistentes después de reiniciar
- ✅ Datos incorrectos o faltantes
- ✅ Problemas de rendimiento severos

#### Información a Proporcionar
1. **Descripción del problema**
2. **Pasos para reproducir**
3. **Captura de pantalla del error**
4. **Información del navegador**
5. **Hora y fecha del incidente**

## 📚 Recursos Adicionales

### Documentación Técnica
- **Guía del Desarrollador**: Para personalización
- **Documentación de API**: Para integraciones
- **Wiki del Proyecto**: Para preguntas frecuentes

### Capacitación
- **Videos Tutoriales**: Disponibles en el portal interno
- **Sesiones de Entrenamiento**: Programadas mensualmente
- **Documentación de Casos de Uso**: Ejemplos prácticos

### Comunidad
- **Foro Interno**: Para compartir mejores prácticas
- **Canal de Slack**: Para preguntas rápidas
- **Newsletter**: Actualizaciones y nuevas funcionalidades

---

**¿Necesitas ayuda?** Contacta al equipo de soporte o consulta la documentación técnica.

*Última actualización: Julio 2024* 