
import argparse, os, shutil, random
from pathlib import Path

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

def list_images(images_dir):
    images = []
    for p in Path(images_dir).rglob('*'):
        if p.suffix.lower() in IMG_EXTS:
            images.append(p)
    return images

def main():
    ap = argparse.ArgumentParser(description="Split images(+labels) into YOLO train/val/test structure.")
    ap.add_argument('--images_dir', required=True, help='Folder containing ALL images (flat or nested).')
    ap.add_argument('--labels_dir', required=False, default=None, help='Folder with YOLO .txt labels (flat or nested). If omitted, only images will be split.')
    ap.add_argument('--out_dir', required=True, help='Output dataset root folder.')
    ap.add_argument('--val', type=float, default=0.15, help='Validation ratio.')
    ap.add_argument('--test', type=float, default=0.0, help='Test ratio.')
    ap.add_argument('--copy', action='store_true', help='Copy (default).')
    ap.add_argument('--move', action='store_true', help='Move instead of copy.')
    ap.add_argument('--seed', type=int, default=42, help='Random seed.')
    args = ap.parse_args()

    random.seed(args.seed)
    op = shutil.move if args.move else shutil.copy2

    images = list_images(args.images_dir)
    if not images:
        raise SystemExit(f"No images found in {args.images_dir}")
    images = sorted(images)
    random.shuffle(images)

    n = len(images)
    n_test = int(n * args.test)
    n_val  = int(n * args.val)
    test_set = set(images[:n_test])
    val_set  = set(images[n_test:n_test+n_val])
    train_set = set(images[n_test+n_val:])

    for split in ['train', 'val', 'test']:
        (Path(args.out_dir)/'images'/split).mkdir(parents=True, exist_ok=True)
        (Path(args.out_dir)/'labels'/split).mkdir(parents=True, exist_ok=True)

    def match_label(img_path: Path):
        if not args.labels_dir: return None
        stem = img_path.stem
        candidates = list(Path(args.labels_dir).rglob(stem + '.txt'))
        return candidates[0] if candidates else None

    missing_labels, no_image_for_label = 0, 0

    all_label_stems = set()
    if args.labels_dir:
        for lp in Path(args.labels_dir).rglob('*.txt'):
            all_label_stems.add(lp.stem)

    for img in images:
        if img in train_set: split = 'train'
        elif img in val_set: split = 'val'
        else: split = 'test'

        dst_img = Path(args.out_dir)/'images'/split/img.name
        op(str(img), str(dst_img))

        if args.labels_dir:
            lbl = match_label(img)
            if lbl and lbl.is_file():
                dst_lbl = Path(args.out_dir)/'labels'/split/(img.stem + '.txt')
                op(str(lbl), str(dst_lbl))
            else:
                missing_labels += 1

    if args.labels_dir:
        used_stems = {p.stem for p in Path(args.out_dir).rglob('labels/*/*.txt')}
        orphans = all_label_stems - used_stems
        no_image_for_label = len(orphans)

    print(f"Total images: {n}")
    print(f"Split -> train: {len(train_set)}, val: {len(val_set)}, test: {len(test_set)}")
    if args.labels_dir:
        print(f"Images missing labels: {missing_labels}")
        print(f"Labels without matching images (orphans): {no_image_for_label}")
    print(f"Done. Dataset at: {args.out_dir}")

if __name__ == '__main__':
    main()
