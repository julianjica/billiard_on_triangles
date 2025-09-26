import matplotlib.pyplot as plt
import numpy as np

def obtain_angles_period():
    print("--- Billiards Trajectory Simulator ---")
    while True:
        try:
            angles_str = input("Enter two angles of the triangle (in degrees), separated by a comma > ")
            alpha, beta = [float(x.strip()) for x in angles_str.split(",")]
            if alpha <= 0 or beta <= 0 or alpha + beta >= 180:
                print("Invalid angles. The two angles must be positive and their sum must be less than 180.")
                continue
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter two numbers separated by a comma.")

    alpha_rad, beta_rad = np.deg2rad(alpha), np.deg2rad(beta)
    gamma_rad = np.pi - (alpha_rad + beta_rad)

    while True:
        try:
            phi_str = input("Enter initial trajectory angle (in degrees) > ")
            phi = float(phi_str)
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    phi_rad = np.deg2rad(phi)

    while True:
        try:
            n_str = input("Enter number of reflections > ")
            n = int(n_str)
            if n <= 0:
                print("Number of reflections must be a positive integer.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    while True:
        save_str = input("Autosave plots to PNG files? (yes/no) > ").lower().strip()
        if save_str in ["yes", "y"]:
            should_save = True
            break
        elif save_str in ["no", "n"]:
            should_save = False
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    print("------------------------------------")
    return (alpha_rad, beta_rad, gamma_rad, phi_rad, n, should_save)

def get_line_segment_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None  # Parallel or collinear

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

    if 1e-9 < t < 1-1e-9 and u > 1e-9:
        return np.array([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
    return None

def reflect_point(p, p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0 and dy == 0:
        return p
    a = (dx**2 - dy**2) / (dx**2 + dy**2)
    b = 2 * dx * dy / (dx**2 + dy**2)
    x_reflected = a * (p[0] - p1[0]) + b * (p[1] - p1[1]) + p1[0]
    y_reflected = b * (p[0] - p1[0]) - a * (p[1] - p1[1]) + p1[1]
    return np.array([x_reflected, y_reflected])

def trace_trajectory(b, n, initial_triangle, initial_angles, phi0):
    path = [{'vertices': initial_triangle, 'iter': 0}]
    current_triangle = initial_triangle
    current_angles = initial_angles

    tan_phi0 = np.tan(phi0)
    if abs(tan_phi0) < 1e-9:
        return []

    traj_p1 = np.array([b, 0])
    traj_p2 = np.array([(2000 + tan_phi0 * b) / tan_phi0, 2000])

    for i in range(n):
        A, B, C = current_triangle
        intersect_ac = get_line_segment_intersection(A, C, traj_p1, traj_p2)
        intersect_bc = get_line_segment_intersection(B, C, traj_p1, traj_p2)

        if intersect_ac is not None:
            B_reflected = reflect_point(B, A, C)
            current_triangle = np.array([C, A, B_reflected])
            path.append({'vertices': current_triangle, 'iter': i + 1})
        elif intersect_bc is not None:
            A_reflected = reflect_point(A, B, C)
            current_triangle = np.array([B, C, A_reflected])
            path.append({'vertices': current_triangle, 'iter': i + 1})
        else:
            break
    return path

def is_degenerate(path, b, tan_phi0):
    m = tan_phi0
    for poly in path:
        for vx, vy in poly['vertices']:
            if abs(vy - m * (vx - b)) < 1e-9:
                return True
    return False

def evolution(alpha, beta, gamma, phi, n, should_save):
    A = np.array([0,0])
    B = np.array([np.sin(gamma) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)), 0])
    C = np.sin(beta) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)) * np.array([np.cos(alpha), np.sin(alpha)])
    x, phi0 = B[0], phi
    initial_triangle = np.vstack((A,B,C))
    initial_angles = (alpha, beta, gamma)

    x_interval = np.linspace(0, x, 100)
    found_towers = []
    tower_data = []
    tan_phi0 = np.tan(phi0)

    print("\nProcessing trajectories to find unique, non-degenerate towers...")
    for b in x_interval:
        path = trace_trajectory(b, n, initial_triangle, initial_angles, phi0)

        if not path or len(path) <= 1:
            continue

        if is_degenerate(path, b, tan_phi0):
            print(f"  -> Discarding degenerate tower for b={b:.4f}")
            continue

        tower_id = frozenset(tuple(sorted(map(tuple, np.round(p['vertices'], 6)))) for p in path)

        if tower_id not in found_towers:
            found_towers.append(tower_id)
            tower_data.append((b, path))

    if not tower_data:
        print("\nNo unique, non-degenerate towers were found.")
        return

    print(f"\nFound {len(tower_data)} unique, non-degenerate towers.")

    for i, (b, path) in enumerate(tower_data):
        print(f"\nPlotting {i+1}/{len(tower_data)} unique tower... (Close plot window to continue, or press Ctrl+C to exit)")
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_title(f"Tower for trajectory starting near b={b:.2f}")
        
        y_max = max(p['vertices'][:,1].max() for p in path) if path else 0

        for poly in path:
            ax.add_patch(plt.Polygon(poly['vertices'], closed=True, facecolor='none', edgecolor='red', linewidth=1))
            centroid = np.mean(poly['vertices'], axis=0)
            ax.text( centroid[0], centroid[1], str(poly['iter']), fontsize=10)
        
        y = np.linspace(0, y_max, 200)
        x_traj = (y + tan_phi0 * b) / tan_phi0
        ax.plot(x_traj, y, color="blue", linestyle='--', linewidth=0.7)
        
        ax.set_aspect('equal', adjustable='box')
        
        if should_save:
            figure_filename = f"images/tower_{i+1}.png"
            try:
                fig.savefig(figure_filename)
                print(f"  -> Saved tower plot to {figure_filename}")
            except Exception as e:
                print(f"  -> Error saving figure: {e}")

        plt.show()

if __name__ == "__main__":
    # Obtain parameters from the user interactively
    alpha, beta, gamma, phi, n, should_save = obtain_angles_period()
    evolution(alpha, beta, gamma, phi, n, should_save)
