
import argparse, yaml
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description="Generate YOLO data.yaml")
    ap.add_argument('--dataset_root', required=True, help='Root that contains images/train, images/val, labels/train, labels/val')
    ap.add_argument('--names', nargs='+', required=True, help='Class names in order, e.g., primary_root lateral_root root_tip')
    ap.add_argument('--out', default='data.yaml', help='Output yaml path')
    args = ap.parse_args()

    root = Path(args.dataset_root)
    data = {
        'train': str(root / 'images' / 'train'),
        'val':   str(root / 'images' / 'val'),
        'names': list(args.names),
    }

    with open(args.out, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote {args.out}")
    print(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

if __name__ == '__main__':
    main()
