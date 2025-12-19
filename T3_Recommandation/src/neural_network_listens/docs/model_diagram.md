```mermaid
flowchart LR
    A[Sources CSV\nclean_tracks + rank_track] --> B[Prétraitement\n- imputation médiane\n- normalisation (z-score)\n- ajout âge du titre\n- log1p(cible)]
    B --> C[Découpage\n80 % entraînement / 20 % test\n+ 10 % validation sur le train]
    C --> D[Modèle MLP\n9 entrées → Dense 256 → ReLU → Dropout 0,1 → Dense 128 → ReLU → Dropout 0,1 → Dense 1]
    D --> E[Entraînement\nSmoothL1Loss\nAdam + ReduceLROnPlateau\nClip gradient 1,0]
    E --> F[Artéfacts\nmodel.pt\nsummary.json\nméta de prétraitement]
    F --> G[Inférence\ntransform_tracks\nprédiction en log\nclamp aux bornes\nexpm1 → écoutes]
```
