# Analizador de Microplásticos

App web local (Streamlit) para detectar y contar microplásticos en imágenes de microscopía de
fluorescencia. Motor **100% local, gratis y sin conexión a internet**: procesamiento de imagen
clásico (OpenCV) por color/brillo/forma/nitidez de borde, con un clasificador liviano
(scikit-learn) que se entrena con tus propias fotos de referencia y con las correcciones que le
hagas. No usa ninguna IA de terceros ni requiere API key.

Permite elegir el tipo de tinción, procesar imágenes individuales o carpetas completas en lote,
comparar resultados visualmente, subir ejemplos de referencia marcados a mano, y corregir al
programa para que mejore en futuras corridas.

## Instalación

```bash
cd Analizador_Microplasticos
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

Se abre en el navegador en `http://localhost:8501`. No hace falta configurar nada más para
empezar: el motor arranca con umbrales por defecto razonables y mejora a medida que lo entrenás.

## Cómo mejora la detección

1. **Entrenamiento**: subís una foto y marcás con círculos (ajustables de tamaño) dónde están
   los microplásticos verdaderos, igual que en tus fotos de referencia con círculo amarillo.
2. **Correcciones**: después de analizar, marcás detecciones que NO eran microplásticos (falsos
   positivos) o dibujás los que faltó marcar (falsos negativos).
3. **Configuración → Recalibrar**: junta todos esos ejemplos y entrena un clasificador por
   tinción. Hasta que haya ejemplos suficientes de ambas clases, se usan umbrales por defecto
   (nitidez de borde + forma compacta) para que la app funcione desde el primer uso.

## Páginas

- **Principal**: subir imágenes (individuales o carpeta local), elegir tinción, analizar en
  lote con barra de progreso y ver el reporte de cada imagen.
- **Comparador**: ver original vs. imagen marcada, con el tamaño de los círculos ajustable.
- **Entrenamiento**: subir fotos de referencia y marcar a mano (círculos ajustables) los
  microplásticos verdaderos.
- **Correcciones**: marcar falsos positivos/negativos de un análisis ya hecho.
- **Configuración**: ajustar el rango de color (H/S/V) por tinción y recalibrar el clasificador.

## Notas

- El procesamiento por carpeta local lee archivos directamente del disco donde corre la app
  (uso local, no un servidor compartido).
- Todos los datos (fotos de entrenamiento, correcciones, clasificadores) quedan guardados en
  `data/` dentro del proyecto.
