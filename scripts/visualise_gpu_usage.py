#!/usr/bin/env python3
"""
GPU Usage Visualization Script
Visualizes GPU monitoring data from nvidia-smi CSV output
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import argparse
import numpy as np

def clean_percentage(value):
    """Remove % sign and convert to float"""
    if isinstance(value, str):
        return float(value.replace('%', '').strip())
    return float(value)

def clean_memory(value):
    """Remove MiB and convert to float"""
    if isinstance(value, str):
        return float(value.replace('MiB', '').strip())
    return float(value)

def clean_power(value):
    """Remove W and convert to float"""
    if isinstance(value, str):
        return float(value.replace('W', '').strip())
    return float(value)

def load_and_process_data(csv_file):
    """Load CSV and process the data"""
    # Read CSV with proper handling of spaces in column names
    df = pd.read_csv(csv_file)
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Clean numeric columns
    df['utilization.gpu [%]'] = df['utilization.gpu [%]'].apply(clean_percentage)
    df['utilization.memory [%]'] = df['utilization.memory [%]'].apply(clean_percentage)
    df['memory.total [MiB]'] = df['memory.total [MiB]'].apply(clean_memory)
    df['memory.free [MiB]'] = df['memory.free [MiB]'].apply(clean_memory)
    df['memory.used [MiB]'] = df['memory.used [MiB]'].apply(clean_memory)
    df['temperature.gpu'] = pd.to_numeric(df['temperature.gpu'])
    df['power.draw [W]'] = df['power.draw [W]'].apply(clean_power)
    
    # Calculate memory usage percentage
    df['memory.used_pct'] = (df['memory.used [MiB]'] / df['memory.total [MiB]']) * 100
    
    return df

def create_visualization(df, output_file=None, show_plot=True):
    """Create comprehensive visualization of GPU metrics"""
    
    # Get unique GPUs
    gpu_ids = df['pci.bus_id'].unique()
    n_gpus = len(gpu_ids)
    
    # Define colors for each GPU
    colors = plt.cm.tab10(np.linspace(0, 1, n_gpus))
    
    # Create figure with subplots
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    fig.suptitle('GPU Monitoring Dashboard', fontsize=16, fontweight='bold')
    
    # Plot 1: GPU Utilization
    ax = axes[0]
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = df[df['pci.bus_id'] == gpu_id]
        ax.plot(gpu_data['timestamp'], gpu_data['utilization.gpu [%]'], 
                label=f'GPU {i} ({gpu_id[-8:]})', color=colors[i], linewidth=2, alpha=0.8)
    ax.set_ylabel('GPU Utilization (%)', fontsize=11, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    ax.set_title('GPU Compute Utilization', fontsize=12, fontweight='bold')
    
    # Plot 2: Memory Usage
    ax = axes[1]
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = df[df['pci.bus_id'] == gpu_id]
        ax.plot(gpu_data['timestamp'], gpu_data['memory.used_pct'], 
                label=f'GPU {i} ({gpu_id[-8:]})', color=colors[i], linewidth=2, alpha=0.8)
    ax.set_ylabel('Memory Usage (%)', fontsize=11, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    ax.set_title('GPU Memory Utilization', fontsize=12, fontweight='bold')
    
    # Plot 3: Temperature
    ax = axes[2]
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = df[df['pci.bus_id'] == gpu_id]
        ax.plot(gpu_data['timestamp'], gpu_data['temperature.gpu'], 
                label=f'GPU {i} ({gpu_id[-8:]})', color=colors[i], linewidth=2, alpha=0.8)
    ax.set_ylabel('Temperature (°C)', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    ax.set_title('GPU Temperature', fontsize=12, fontweight='bold')
    
    # Plot 4: Power Draw
    ax = axes[3]
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = df[df['pci.bus_id'] == gpu_id]
        ax.plot(gpu_data['timestamp'], gpu_data['power.draw [W]'], 
                label=f'GPU {i} ({gpu_id[-8:]})', color=colors[i], linewidth=2, alpha=0.8)
    ax.set_ylabel('Power Draw (W)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Time', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    ax.set_title('GPU Power Consumption', fontsize=12, fontweight='bold')
    
    # Format x-axis for all subplots
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save if output file specified
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {output_file}")
    
    # Show plot if requested
    if show_plot:
        plt.show()
    
    return fig

def print_summary_statistics(df):
    """Print summary statistics for all GPUs"""
    print("\n" + "="*80)
    print("GPU MONITORING SUMMARY STATISTICS")
    print("="*80)
    
    gpu_ids = df['pci.bus_id'].unique()
    
    for i, gpu_id in enumerate(gpu_ids):
        gpu_data = df[df['pci.bus_id'] == gpu_id]
        
        print(f"\n📊 GPU {i} ({gpu_id})")
        print(f"   Name: {gpu_data['name'].iloc[0]}")
        print(f"   Total Memory: {gpu_data['memory.total [MiB]'].iloc[0]:.0f} MiB")
        print(f"\n   GPU Utilization:")
        print(f"      Mean: {gpu_data['utilization.gpu [%]'].mean():.2f}%")
        print(f"      Max:  {gpu_data['utilization.gpu [%]'].max():.2f}%")
        print(f"      Min:  {gpu_data['utilization.gpu [%]'].min():.2f}%")
        print(f"\n   Memory Usage:")
        print(f"      Mean: {gpu_data['memory.used_pct'].mean():.2f}%")
        print(f"      Max:  {gpu_data['memory.used_pct'].max():.2f}%")
        print(f"      Peak: {gpu_data['memory.used [MiB]'].max():.0f} MiB")
        print(f"\n   Temperature:")
        print(f"      Mean: {gpu_data['temperature.gpu'].mean():.1f}°C")
        print(f"      Max:  {gpu_data['temperature.gpu'].max():.1f}°C")
        print(f"      Min:  {gpu_data['temperature.gpu'].min():.1f}°C")
        print(f"\n   Power Draw:")
        print(f"      Mean: {gpu_data['power.draw [W]'].mean():.2f} W")
        print(f"      Max:  {gpu_data['power.draw [W]'].max():.2f} W")
        print(f"      Min:  {gpu_data['power.draw [W]'].min():.2f} W")
    
    # Overall statistics
    print(f"\n" + "-"*80)
    print(f"📈 OVERALL STATISTICS")
    print(f"   Monitoring Duration: {(df['timestamp'].max() - df['timestamp'].min()).total_seconds():.1f} seconds")
    print(f"   Number of GPUs: {len(gpu_ids)}")
    print(f"   Total Samples: {len(df)}")
    print(f"   Samples per GPU: {len(df) // len(gpu_ids)}")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Visualize GPU monitoring data from nvidia-smi CSV output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - display plot
  python visualize_gpu_usage.py gpu_usage_95506.csv
  
  # Save to file without displaying
  python visualize_gpu_usage.py gpu_usage_95506.csv -o gpu_plot.png --no-show
  
  # Display plot and save
  python visualize_gpu_usage.py gpu_usage_95506.csv -o gpu_plot.png
        """
    )
    parser.add_argument('csv_file', type=str, help='Path to the GPU usage CSV file')
    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output file path for saving the plot (e.g., plot.png)')
    parser.add_argument('--no-show', action='store_true',
                       help='Do not display the plot (useful when only saving)')
    parser.add_argument('--no-stats', action='store_true',
                       help='Do not print summary statistics')
    
    args = parser.parse_args()
    
    # Check if file exists
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: File '{args.csv_file}' not found!")
        return 1
    
    print(f"Loading data from: {args.csv_file}")
    df = load_and_process_data(args.csv_file)
    
    print(f"Successfully loaded {len(df)} records for {len(df['pci.bus_id'].unique())} GPU(s)")
    
    # Print statistics unless disabled
    if not args.no_stats:
        print_summary_statistics(df)
    
    # Create visualization
    print("\nGenerating visualization...")
    create_visualization(df, output_file=args.output, show_plot=not args.no_show)
    
    print("Done!")
    return 0

if __name__ == "__main__":
    exit(main())
