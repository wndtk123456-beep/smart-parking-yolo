import config


def main():
    names = [
        name
        for name, _ in sorted(config.CLASS_MAP.items(), key=lambda item: item[1])
    ]
    lines = [
        f"path: {config.DATASET_ROOT.resolve().as_posix()}",
        "train: images/train",
        "val: images/val",
        f"nc: {len(names)}",
        "names:",
    ]
    lines.extend(f"  {index}: {name}" for index, name in enumerate(names))
    config.YAML_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {config.YAML_PATH}")


if __name__ == "__main__":
    main()

