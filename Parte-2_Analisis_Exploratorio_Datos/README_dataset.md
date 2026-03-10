# Generación de dataset con pandas (CUB-200-2011)

Este script crea un dataset tabular principal por imagen y exporta tablas auxiliares de partes y atributos.

## Archivos generados

Ejecutando `generate_dataset_from_images.py` se crean:

- `cub200_dataset.csv`: dataset principal por imagen.
- `cub200_part_locations.csv`: ubicaciones de partes por imagen/parte.
- `cub200_image_attribute_votes.csv`: anotaciones de atributos por imagen/atributo/worker.
- `cub200_class_attribute_scores.csv`: matriz continua de atributos por clase.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python generate_dataset_from_images.py
```

Con opciones:

```bash
python generate_dataset_from_images.py \
  --cub-root ./CUB_200_2011/CUB_200_2011 \
  --images-root ./CUB_200_2011/CUB_200_2011/images \
  --output-dir . \
  --prefix cub200 \
  --sep ,
```

Para salida TSV:

```bash
python generate_dataset_from_images.py --sep "\\t"
```
