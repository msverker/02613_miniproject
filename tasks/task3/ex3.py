import matplotlib.pyplot as plt
import numpy as np

def plot_heatmaps(all_u, all_interior_mask, building_ids, selected_ids=['14317', '28672', '7528', '7459']):
    
    fig, axes = plt.subplots(1, 4, figsize=(12, 3))
    
    for i, bid in enumerate(selected_ids):
        try:
            idx = building_ids.index(bid)
        except ValueError:
            raise ValueError(f"Building ID {bid} not found in building_ids.")
        
        u = all_u[idx, 1:-1, 1:-1]
        interior_mask = all_interior_mask[idx]
        
        u_display = np.where(interior_mask, u, np.nan)
        
        axes[i].set_facecolor('black')
        
        # Plot heatmap
        im = axes[i].imshow(u_display, cmap='inferno')
        axes[i].set_title(f'Building ID: {bid}', fontsize=10, color='white')
        axes[i].set_xlabel('X', fontsize=8, color='white')
        axes[i].set_ylabel('Y', fontsize=8, color='white')
        axes[i].set_aspect('equal')
        axes[i].tick_params(colors='white', labelsize=6)
        axes[i].set_facecolor('black')
        cbar = plt.colorbar(im, ax=axes[i], fraction=0.046, pad=0.04)
        cbar.set_label('Temperature', fontsize=8, color='white')
        cbar.ax.tick_params(labelsize=6, colors='white')
    
    # Adjust layout to prevent overlap
    plt.tight_layout(pad=1.0, w_pad=2.0)
    plt.savefig('heatmap_subplots.png', dpi=300, bbox_inches='tight')
    plt.close()