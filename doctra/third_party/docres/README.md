### DocRes Inference Bundle

This folder is a standalone inference bundle extracted from the original `DocRes` repository. It contains only the files required for inference so you can copy and use it directly in other projects.

- Original repository: [ZZZHANG-jx/DocRes](https://github.com/ZZZHANG-jx/DocRes)
- Paper: [DocRes: A Generalist Model Toward Unifying Document Image Restoration Tasks](https://arxiv.org/abs/2405.04408)

### Supported tasks
- dewarping
- deshadowing
- appearance
- deblurring
- binarization
- end2end (pipeline: dewarping → deshadowing → appearance)

### Checkpoints
- DocRes weights: `./checkpoints/docres.pkl`
- MBD segmentation weights: `./data/MBD/checkpoint/mbd.pkl`

If you need to download the weights, see the original README's Inference section or use:
- DocRes weights: [OneDrive link](https://1drv.ms/f/s!Ak15mSdV3Wy4iahoKckhDPVP5e2Czw?e=iClwdK)
- MBD weights: [OneDrive link](https://1drv.ms/f/s!Ak15mSdV3Wy4iahoKckhDPVP5e2Czw?e=iClwdK)

### Usage (from this folder)
1. Place inputs in `./input` or pass `--im_path` to a file/folder.
2. Ensure checkpoints exist at the paths above (or pass `--model_path` for DocRes and update the MBD path inside `inference.py` if needed).
3. Run inference. Examples:

```bash
# Windows PowerShell / CMD (examples)
python inference.py --im_path .\input\for_dewarping.png --task dewarping --save_dtsprompt 1
python inference.py --im_path .\input --task appearance --out_folder .\restorted
```

Arguments (from original):
- `--im_path`: path of input document image or a directory
- `--task`: one of `dewarping`, `deshadowing`, `appearance`, `deblurring`, `binarization`, `end2end`
- `--save_dtsprompt`: whether to save the DTSPrompt (0/1)

### Environment
Install dependencies (preferably in a virtual environment):

```bash
pip install -r requirements.txt
```

### Attribution
This inference bundle is assembled from the original `DocRes` codebase and is intended for inference-only usage in downstream repositories. Please cite the paper if you use this in academic work.
