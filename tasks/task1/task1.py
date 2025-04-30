import numpy as np
import sys
from os.path import join
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def create_subplots(all_u0, all_interior_mask, building_ids, save_path):
    N = len(building_ids)
    max_cols = min(N, 8)
    
    rows, cols = 2, max_cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*4))
    
    if cols == 1:
        axes = np.array([axes]).T
    
    for i in range(min(N, max_cols)):
        # Top row: Buildings
        axes[0, i].imshow(all_u0[i], cmap='viridis')
        axes[0, i].set_title(f'Building ID #{building_ids[i]}')
        axes[0, i].axis('off')
        
        # Bottom row: Masks
        axes[1, i].imshow(all_interior_mask[i], cmap='gray')
        axes[1, i].axis('off')
    
    # Hide unused columns if N < max_cols
    for i in range(min(N, max_cols), cols):
        axes[0, i].axis('off')
        axes[1, i].axis('off')
    
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    return None

def main():
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    SAVE_PATH = 'building_plots.png'
    
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    
    if len(sys.argv) >= 3:
        SAVE_PATH = sys.argv[2]
    
    building_ids = np.random.choice(building_ids, size=min(N, len(building_ids)), replace=False).tolist()

    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask
    
    create_subplots(all_u0, all_interior_mask, building_ids, SAVE_PATH)

if __name__ == "__main__":
    main()