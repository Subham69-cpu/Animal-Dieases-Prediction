"""Train CNN on dataset/cnn_flat and save cnn_model/model.h5 + class_indices.json."""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def build_model(num_classes: int, img_size: int):
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential(
        [
            layers.Input(shape=(img_size, img_size, 3)),
            layers.Conv2D(32, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Conv2D(128, 3, activation="relu", padding="same"),
            layers.MaxPooling2D(),
            layers.Dropout(0.25),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.4),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--img-size", type=int, default=128)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    data_dir = ROOT / "dataset" / "cnn_flat"
    out_dir = ROOT / "cnn_model"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not data_dir.is_dir() or not any(data_dir.iterdir()):
        print("Run: python scripts/generate_datasets.py first", file=sys.stderr)
        sys.exit(1)

    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch,
    )
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch,
    )
    class_names = list(train_ds.class_names)
    num_classes = len(class_names)
    train_ds = train_ds.cache().prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(tf.data.AUTOTUNE)

    aug = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.08),
            layers.RandomContrast(0.1),
        ]
    )

    def augment(image, label):
        return aug(image, training=True), label

    train_ds = train_ds.map(augment, num_parallel_calls=tf.data.AUTOTUNE)

    model = build_model(num_classes, args.img_size)
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs)

    model_path = out_dir / "model.h5"
    model.save(model_path)
    indices = {name: i for i, name in enumerate(class_names)}
    with open(out_dir / "class_indices.json", "w", encoding="utf-8") as f:
        json.dump(indices, f, indent=2)
    print("Saved", model_path, "classes:", len(class_names))


if __name__ == "__main__":
    main()
