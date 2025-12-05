#!/usr/bin/env python3
"""
Visualize bus travel time data collected from TDX API.

Generates:
  - Travel time distribution by route
  - Travel time by operator
  - Distance vs time scatter plot
  - Top 20 slowest/fastest routes

Usage:
  python visualize_travel_time.py --input data/travel_times.csv --output-dir figs/
"""
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def load_data(csv_path: str) -> pd.DataFrame:
    """Load travel time CSV."""
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from {csv_path}")
    return df


def plot_travel_time_distribution(df: pd.DataFrame, out_dir: str):
    """Plot distribution of travel times."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Remove nulls
    times = df['TravelTime'].dropna()
    
    ax.hist(times, bins=50, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Travel Time (seconds)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Travel Times (Segment Level)')
    ax.grid(True, alpha=0.3)
    
    out_path = Path(out_dir) / 'travel_time_distribution.png'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()


def plot_travel_time_by_operator(df: pd.DataFrame, out_dir: str):
    """Plot average travel times by operator."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Group by operator and get mean travel time
    operator_times = df.groupby('OperatorCode')['TravelTime'].agg(['mean', 'count']).reset_index()
    operator_times = operator_times[operator_times['count'] > 0].sort_values('mean', ascending=False)
    
    ax.barh(operator_times['OperatorCode'], operator_times['mean'], color='steelblue', edgecolor='black')
    ax.set_xlabel('Average Travel Time (seconds)')
    ax.set_ylabel('Operator Code')
    ax.set_title('Average Travel Time by Operator')
    ax.grid(True, alpha=0.3, axis='x')
    
    out_path = Path(out_dir) / 'travel_time_by_operator.png'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()


def plot_distance_vs_time(df: pd.DataFrame, out_dir: str):
    """Scatter plot: distance vs travel time."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Remove nulls
    valid = df[['Distance', 'TravelTime']].dropna()
    
    ax.scatter(valid['Distance'], valid['TravelTime'], alpha=0.5, s=20)
    ax.set_xlabel('Distance (meters)')
    ax.set_ylabel('Travel Time (seconds)')
    ax.set_title('Distance vs Travel Time')
    ax.grid(True, alpha=0.3)
    
    out_path = Path(out_dir) / 'distance_vs_time.png'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()


def plot_top_routes(df: pd.DataFrame, out_dir: str):
    """Plot top 20 slowest and fastest average travel time routes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Group by route
    route_times = df.groupby(['RouteID', 'RouteName_Zh', 'Direction'])['TravelTime'].mean().reset_index()
    route_times.columns = ['RouteID', 'RouteName_Zh', 'Direction', 'AvgTime']
    route_times = route_times.dropna(subset=['AvgTime'])
    
    # Top 20 slowest
    slowest = route_times.nlargest(20, 'AvgTime')
    slowest_label = slowest['RouteID'].astype(str) + ' (' + slowest['Direction'].astype(str) + ')'
    ax1.barh(range(len(slowest)), slowest['AvgTime'], color='coral', edgecolor='black')
    ax1.set_yticks(range(len(slowest)))
    ax1.set_yticklabels(slowest_label, fontsize=8)
    ax1.set_xlabel('Average Travel Time (seconds)')
    ax1.set_title('Top 20 Slowest Routes')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Top 20 fastest
    fastest = route_times.nsmallest(20, 'AvgTime')
    fastest_label = fastest['RouteID'].astype(str) + ' (' + fastest['Direction'].astype(str) + ')'
    ax2.barh(range(len(fastest)), fastest['AvgTime'], color='lightgreen', edgecolor='black')
    ax2.set_yticks(range(len(fastest)))
    ax2.set_yticklabels(fastest_label, fontsize=8)
    ax2.set_xlabel('Average Travel Time (seconds)')
    ax2.set_title('Top 20 Fastest Routes')
    ax2.grid(True, alpha=0.3, axis='x')
    
    out_path = Path(out_dir) / 'top_routes.png'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {out_path}")
    plt.close()


def generate_summary(df: pd.DataFrame, out_dir: str):
    """Generate text summary of travel time statistics."""
    out_path = Path(out_dir) / 'travel_time_summary.txt'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with out_path.open('w', encoding='utf-8') as f:
        f.write("=== Bus Travel Time Summary ===\n\n")
        
        # Overall stats
        times = df['TravelTime'].dropna()
        f.write(f"Total segments: {len(df)}\n")
        f.write(f"Segments with travel time: {len(times)}\n")
        f.write(f"Mean travel time: {times.mean():.1f} seconds\n")
        f.write(f"Median travel time: {times.median():.1f} seconds\n")
        f.write(f"Std dev: {times.std():.1f} seconds\n")
        f.write(f"Min: {times.min():.1f} seconds\n")
        f.write(f"Max: {times.max():.1f} seconds\n\n")
        
        # By operator
        f.write("=== By Operator ===\n")
        operator_stats = df.groupby('OperatorCode')['TravelTime'].agg(['count', 'mean', 'min', 'max'])
        f.write(operator_stats.to_string())
        f.write("\n\n")
        
        # By route
        f.write("=== Top 10 Routes by Avg Travel Time ===\n")
        route_stats = df.groupby(['RouteID', 'RouteName_Zh'])['TravelTime'].agg(['count', 'mean']).sort_values('mean', ascending=False).head(10)
        f.write(route_stats.to_string())
        f.write("\n")
    
    print(f"Saved summary: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize bus travel time data")
    parser.add_argument('--input', default='data/travel_times.csv', help='Input CSV file')
    parser.add_argument('--output-dir', default='figs/', help='Output directory for plots')
    args = parser.parse_args()

    # Load data
    df = load_data(args.input)
    
    print("\nGenerating visualizations...")
    plot_travel_time_distribution(df, args.output_dir)
    plot_travel_time_by_operator(df, args.output_dir)
    plot_distance_vs_time(df, args.output_dir)
    plot_top_routes(df, args.output_dir)
    generate_summary(df, args.output_dir)
    
    print(f"\n✓ All visualizations saved to {args.output_dir}")


if __name__ == '__main__':
    main()
