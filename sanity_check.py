
import argparse, random
from pathlib import Path

def parse_label_line(line):
    parts = line.strip().split()
    if len(parts) != 5: return None
    try:
        cls = int(float(parts[0]))
        vals = [float(x) for x in parts[1:]]
        if not all(0.0 <= v <= 1.0 for v in vals):
            return None
        return cls, vals
    except:
        return None

def main():
    ap = argparse.ArgumentParser(description="Basic YOLO dataset sanity checks")
    ap.add_argument('--dataset_root', required=True)
    ap.add_argument('--num_examples', type=int, default=5)
    ap.add_argument('--num_classes', type=int, default=None, help='Optional; check class id range [0, num_classes-1]')
    args = ap.parse_args()

    root = Path(args.dataset_root)
    issues = 0

    for split in ['train', 'val', 'test']:
        img_dir = root / 'images' / split
        lbl_dir = root / 'labels' / split
        if not img_dir.exists():
            print(f"[WARN] Missing {img_dir}")
            continue
        imgs = list(img_dir.glob('*'))
        lbls = list(lbl_dir.glob('*.txt')) if lbl_dir.exists() else []
        print(f"[{split}] images={len(imgs)} labels={len(lbls)}")

        miss = 0
        for img in imgs:
            if not (lbl_dir / (img.stem + '.txt')).exists():
                miss += 1
        if miss:
            print(f"  -> {miss} images missing labels")
            issues += miss

        bad = 0
        for lf in lbls:
            with open(lf, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.read().strip().splitlines()
            for ln in lines:
                parsed = parse_label_line(ln)
                if parsed is None:
                    bad += 1
                elif args.num_classes is not None and not (0 <= parsed[0] < args.num_classes):
                    bad += 1
        if bad:
            print(f"  -> {bad} malformed/out-of-range label lines")
            issues += bad

    examples = []
    for split in ['train', 'val', 'test']:
        img_dir = root / 'images' / split
        if img_dir.exists():
            imgs = list(img_dir.glob('*'))
            examples.extend([str(p) for p in random.sample(imgs, min(args.num_examples, len(imgs)))])
    if examples:
        print("Sample images to visually verify:")
        for p in examples:
            print("  ", p)

    if issues == 0:
        print("Sanity check passed with no issues found.")
    else:
        print(f"Sanity check found {issues} potential issues.")

if __name__ == '__main__':
    main()
