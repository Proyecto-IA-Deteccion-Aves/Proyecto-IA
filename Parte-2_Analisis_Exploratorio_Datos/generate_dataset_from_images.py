from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


def read_id_name_file(file_path: Path, id_col: str, name_col: str) -> pd.DataFrame:
	rows: list[tuple[int, str]] = []
	with file_path.open("r", encoding="utf-8") as file:
		for line in file:
			line = line.strip()
			if not line:
				continue
			parts = line.split(maxsplit=1)
			if len(parts) == 1:
				rows.append((int(parts[0]), ""))
			else:
				rows.append((int(parts[0]), parts[1]))
	return pd.DataFrame(rows, columns=[id_col, name_col])


def load_base_dataset(cub_root: Path, images_root: Path) -> pd.DataFrame:
	images = pd.read_csv(
		cub_root / "images.txt",
		sep=r"\s+",
		header=None,
		names=["image_id", "image_path"],
	)

	classes = pd.read_csv(
		cub_root / "classes.txt",
		sep=r"\s+",
		header=None,
		names=["class_id", "class_name"],
	)

	labels = pd.read_csv(
		cub_root / "image_class_labels.txt",
		sep=r"\s+",
		header=None,
		names=["image_id", "class_id"],
	)

	split = pd.read_csv(
		cub_root / "train_test_split.txt",
		sep=r"\s+",
		header=None,
		names=["image_id", "is_train"],
	)

	boxes = pd.read_csv(
		cub_root / "bounding_boxes.txt",
		sep=r"\s+",
		header=None,
		names=["image_id", "bbox_x", "bbox_y", "bbox_width", "bbox_height"],
	)

	dataset = (
		images.merge(labels, on="image_id", how="left")
		.merge(classes, on="class_id", how="left")
		.merge(split, on="image_id", how="left")
		.merge(boxes, on="image_id", how="left")
	)

	dataset["split"] = dataset["is_train"].map({1: "train", 0: "test"})
	dataset["class_folder"] = dataset["image_path"].str.split("/", n=1).str[0]
	dataset["image_name"] = dataset["image_path"].str.split("/").str[-1]
	dataset["image_full_path"] = dataset["image_path"].apply(
		lambda relative_path: str(images_root / relative_path)
	)
	dataset["bbox_area"] = dataset["bbox_width"] * dataset["bbox_height"]

	return dataset[
		[
			"image_id",
			"class_id",
			"class_name",
			"class_folder",
			"image_name",
			"image_path",
			"image_full_path",
			"split",
			"is_train",
			"bbox_x",
			"bbox_y",
			"bbox_width",
			"bbox_height",
			"bbox_area",
		]
	]


def load_parts_summary(cub_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
	parts_dir = cub_root / "parts"

	part_names = read_id_name_file(parts_dir / "parts.txt", "part_id", "part_name")

	part_locs = pd.read_csv(
		parts_dir / "part_locs.txt",
		sep=r"\s+",
		header=None,
		names=["image_id", "part_id", "part_x", "part_y", "visible"],
	).merge(part_names, on="part_id", how="left")

	summary = (
		part_locs.groupby("image_id", as_index=False)
		.agg(
			parts_annotated_count=("part_id", "count"),
			parts_visible_count=("visible", "sum"),
		)
		.assign(parts_visible_ratio=lambda df: df["parts_visible_count"] / df["parts_annotated_count"])
	)

	return summary, part_locs


def resolve_attributes_file(cub_root: Path) -> Optional[Path]:
	candidates = [
		cub_root / "attributes" / "attributes.txt",
		cub_root.parent / "attributes.txt",
	]
	for path in candidates:
		if path.exists():
			return path
	return None


def split_attribute_name(attribute_name: str) -> tuple[str, str]:
	parts = attribute_name.split("::", maxsplit=1)
	if len(parts) == 2:
		return parts[0].strip(), parts[1].strip()
	return attribute_name.strip(), ""


def load_attributes_by_category(cub_root: Path) -> pd.DataFrame:
	attributes_dir = cub_root / "attributes"

	attributes_file = resolve_attributes_file(cub_root)
	if attributes_file is None:
		raise FileNotFoundError("No se encontró attributes.txt en rutas esperadas.")

	attribute_names = read_id_name_file(attributes_file, "attribute_id", "attribute_name")

	certainties = read_id_name_file(
		attributes_dir / "certainties.txt", "certainty_id", "certainty_name"
	)

	image_attribute_votes = pd.read_csv(
		attributes_dir / "image_attribute_labels.txt",
		sep=r"\s+",
		usecols=[0, 1, 2, 3, 4],
		engine="python",
		header=None,
		names=["image_id", "attribute_id", "is_present", "certainty_id", "annotation_time"],
	)

	image_attribute_votes = image_attribute_votes.merge(attribute_names, on="attribute_id", how="left")
	image_attribute_votes = image_attribute_votes.merge(certainties, on="certainty_id", how="left")

	attribute_name_map = attribute_names.copy()
	attribute_name_map[["attribute_category", "attribute_value"]] = attribute_name_map[
		"attribute_name"
	].apply(split_attribute_name).apply(pd.Series)

	per_image_attribute = (
		image_attribute_votes.groupby(["image_id", "attribute_id"], as_index=False)
		.agg(is_present_mean=("is_present", "mean"))
	)

	per_image_attribute = per_image_attribute.merge(
		attribute_name_map[["attribute_id", "attribute_category", "attribute_value"]],
		on="attribute_id",
		how="left",
	)

	best_attribute_per_category = (
		per_image_attribute.sort_values(["image_id", "attribute_category", "is_present_mean", "attribute_id"])
		.groupby(["image_id", "attribute_category"], as_index=False)
		.tail(1)
	)

	attributes_by_category = best_attribute_per_category.pivot(
		index="image_id",
		columns="attribute_category",
		values="attribute_value",
	).fillna("")

	attributes_by_category.columns.name = None
	attributes_by_category = attributes_by_category.reset_index()

	return attributes_by_category


def build_dataset(cub_root: Path, images_root: Path) -> pd.DataFrame:
	base_dataset = load_base_dataset(cub_root, images_root)

	parts_summary, part_locs = load_parts_summary(cub_root)
	_ = part_locs
	attributes_by_category = load_attributes_by_category(cub_root)

	dataset = (
		base_dataset.merge(parts_summary, on="image_id", how="left")
		.merge(attributes_by_category, on="image_id", how="left")
	)

	attribute_category_cols = [
		col for col in attributes_by_category.columns if col != "image_id"
	]
	if attribute_category_cols:
		dataset[attribute_category_cols] = dataset[attribute_category_cols].fillna("")

	return dataset


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Genera un dataset tabular completo del CUB-200-2011 usando pandas."
	)
	parser.add_argument(
		"--cub-root",
		type=Path,
		default=Path(__file__).resolve().parent / "CUB_200_2011" / "CUB_200_2011",
		help="Ruta al directorio con metadatos (images.txt, classes.txt, etc.).",
	)
	parser.add_argument(
		"--images-root",
		type=Path,
		default=Path(__file__).resolve().parent
		/ "CUB_200_2011"
		/ "CUB_200_2011"
		/ "images",
		help="Ruta raíz de imágenes para construir image_full_path.",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=Path(__file__).resolve().parent / "cub200_dataset.csv",
		help="Ruta del CSV de salida único.",
	)
	parser.add_argument(
		"--sep",
		type=str,
		default=",",
		help="Separador de salida para CSV. Usa '\\t' para tabulado.",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	dataset = build_dataset(args.cub_root, args.images_root)

	output_path = args.output.resolve()
	output_path.parent.mkdir(parents=True, exist_ok=True)
	separator = "\t" if args.sep == "\\t" else args.sep

	dataset.to_csv(output_path, index=False, sep=separator)

	attribute_category_cols = [col for col in dataset.columns if col.startswith("has_")]
	print(f"Dataset generado: {output_path}")
	print(f"Filas dataset principal: {len(dataset)} | Columnas: {len(dataset.columns)}")
	print(f"Columnas de categorías de atributos: {len(attribute_category_cols)}")
	print(f"Train: {(dataset['split'] == 'train').sum()} | Test: {(dataset['split'] == 'test').sum()}")


if __name__ == "__main__":
	main()
