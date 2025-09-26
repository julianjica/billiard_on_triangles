import matplotlib.pyplot as plt
import numpy as np

def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - \
          (q[0] - p[0]) * (r[1] - q[1])
    if abs(val) < 1e-9: return 0
    return 1 if val > 0 else 2

def on_segment(p, q, r):
    if (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
        q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])):
        return True
    return False

def segments_intersect(p1, q1, p2, q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if (o1 != o2 and o3 != o4): 
        return True
    if (o1 == 0 and on_segment(p1, p2, q1)): return True
    if (o2 == 0 and on_segment(p1, q2, q1)): return True
    if (o3 == 0 and on_segment(p2, p1, q2)): return True
    if (o4 == 0 and on_segment(p2, q1, q2)): return True
    return False

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

    alpha_rad = alpha * np.pi / 180
    beta_rad = beta * np.pi / 180
    gamma_rad = np.pi - (alpha_rad + beta_rad)

    while True:
        try:
            phi_str = input("Enter initial trajectory angle (in degrees) > ")
            phi = float(phi_str)
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    phi_rad = phi * np.pi / 180

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

    print("------------------------------------")
    return (alpha_rad, beta_rad, gamma_rad, phi_rad, n)

def evolution(alpha, beta, gamma, phi, n):
    # First triangle
    A = np.array([0,0])
    B = np.array([np.sin(gamma) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)), 0])
    C = np.sin(beta) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)) \
            * np.array([np.cos(alpha), np.sin(alpha)])
    # Storing for later
    x, phi0 = B[0], phi

    initial_triangle = np.vstack((A,B,C))

    # We will store all generated polygons here, with their iteration number
    all_polygons = []
    all_polygons.append({'vertices': initial_triangle, 'iter': 0})


    triangle_list = [[(initial_triangle, (alpha, beta, gamma), phi)]]
    # And the next triangles
    for ii in range(n):
        m = []
        # For each triangle in the end of the queue, we must check
        # which reflections are generated, given the trajectory.
        if not triangle_list[-1]: break
        for triangle in triangle_list[-1]:
            A, B, C = triangle[0]
            alpha, beta, gamma = triangle[1]
            phi = triangle[2]
            if phi > alpha:
                v = (A - B) - np.dot(A - B, A - C) / np.linalg.norm(A - C) ** 2 * (A - C)
                v = v / np.linalg.norm(v)
                new_triangle = np.vstack((C, A, B + 2 * np.linalg.norm(A - B) * np.sin(alpha) * v))

                all_polygons.append({'vertices': new_triangle, 'iter': ii + 1})
                m.append((new_triangle, (gamma, alpha, beta), np.pi+alpha-phi))

            if phi < np.pi - beta:
                v = (C - A) - np.dot(C - A, C - B) / np.linalg.norm(C - B) ** 2 * (C - B)
                v = v / np.linalg.norm(v)
                new_triangle = np.vstack((B, C, A + 2 * np.linalg.norm(A - B) * np.sin(beta) * v))

                all_polygons.append({'vertices': new_triangle, 'iter': ii + 1})
                m.append((new_triangle, (beta, gamma, alpha), np.pi-beta-phi))

        triangle_list.append(m)

    # Finding y_max to plot trajectory lines
    y_max = 0
    if all_polygons:
        y_max = max(poly['vertices'][:,1].max() for poly in all_polygons)


    # Now, filter the polygons that intersect with the trajectory lines
    intersected_polygons = []
    tan_phi0 = np.tan(phi0)
    x_interval = np.linspace(0, x, 10)
    border_bs = [x_interval[0], x_interval[-1]]

    for poly in all_polygons:
        vertices = poly['vertices']
        edges = [(vertices[0], vertices[1]), (vertices[1], vertices[2]), (vertices[2], vertices[0])]

        intersection_found = False
        for b in border_bs:
            m = tan_phi0
            if m == 0: continue

            T1 = (b, 0)
            T2 = (y_max / m + b, y_max)
            
            for p1, p2 in edges:
                if segments_intersect(p1, p2, T1, T2):
                    intersected_polygons.append(poly)
                    intersection_found = True
                    break
            if intersection_found:
                break
    
    # The first polygon should always be plotted
    if all_polygons and all_polygons[0] not in intersected_polygons:
        intersected_polygons.insert(0, all_polygons[0])

    # Remove duplicates by creating a new list
    unique_polygons = []
    seen_ids = set()
    for poly in intersected_polygons:
        rounded_vertices = np.round(poly['vertices'], decimals=6)
        poly_id = tuple(sorted(tuple(map(tuple, rounded_vertices))))
        if poly_id not in seen_ids:
            unique_polygons.append(poly)
            seen_ids.add(poly_id)


    # Now plot everything
    plt.figure(111)

    # Plot the intersected polygons
    for poly in unique_polygons:
        plt.gca().add_patch(plt.Polygon(poly['vertices'], closed=True, facecolor='none', edgecolor='red', linewidth=2))
        centroid = np.mean(poly['vertices'], axis=0)
        plt.text(centroid[0], centroid[1], str(poly['iter']), fontsize=12)

    # Plotting trajectory lines
    for b in x_interval:
        y = np.linspace(0, y_max)
        x_traj = (y + np.tan(phi0) * b) / np.tan(phi0)
        plt.plot(x_traj, y, color = "blue")
    
    plt.axis('scaled')
    plt.show()

if __name__ == "__main__":
    alpha, beta, gamma, phi, n = obtain_angles_period()
    evolution(alpha, beta, gamma, phi, n)