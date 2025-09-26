import matplotlib.pyplot as plt
import numpy as np

def obtain_angles_period():
    # Obtaining and transforming angles
    alpha, beta = [float(x) for x in\
            input("Enter two angles of the triangle (in degrees) > ").split(",")]
    alpha, beta = [x * np.pi / 180 for x in (alpha, beta)]
    gamma = np.pi - (alpha + beta)

    # Initial trajectory angle
    phi = float(input("Enter initial trajectory angle (in degrees) > ")) * np.pi / 180

    # Obtaining number of periods
    n = int(input("Enter number of periods > "))

    return (alpha, beta, gamma, phi, n)

def evolution(alpha, beta, gamma, phi, n):
    # First triangle
    A = np.array([0,0])
    B = np.array([np.sin(gamma) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)), 0])
    C = np.sin(beta) / (np.sin(alpha) + np.sin(beta) + np.sin(gamma)) \
            * np.array([np.cos(alpha), np.sin(alpha)])
    # Storing for later
    x, phi0 = B[0], phi

    triangle = np.vstack((A,B,C))
    plt.figure(111)
    plt.gca().add_patch(plt.Polygon(triangle, closed=True, facecolor='none',
                                    edgecolor='red', linewidth=2))

    triangle_list = [[(triangle, (alpha, beta, gamma), phi)]]
    # And the next triangles
    for ii in range(n):
        m = []
        # For each triangle in the end of the queue, we must check
        # which reflections are generated, given the trajectory.
        for triangle in triangle_list[-1]:
            A, B, C = triangle[0]
            alpha, beta, gamma = triangle[1]
            phi = triangle[2]
            if phi > alpha:
                v = (A - B) - np.dot(A - B, A - C) / np.linalg.norm(A - C) ** 2 * (A - C)
                v = v / np.linalg.norm(v)
                new_triangle = np.vstack((C, A, B + 2 * np.linalg.norm(A - B) * np.sin(alpha) * v))
                    
                centroid = np.mean(new_triangle, axis=0)
                plt.text(centroid[0], centroid[1], str(ii + 1), fontsize=12)
                plt.gca().add_patch(plt.Polygon(new_triangle, closed=True, facecolor='none',
                                                edgecolor='red', linewidth=2))
                m.append((new_triangle, (gamma, alpha, beta), np.pi+alpha-phi))
            if phi < np.pi - beta:
                v = (C - A) - np.dot(C - A, C - B) / np.linalg.norm(C - B) ** 2 * (C - B)
                v = v / np.linalg.norm(v)
                new_triangle = np.vstack((B, C, A + 2 * np.linalg.norm(A - B) * np.sin(beta) * v))

                centroid = np.mean(new_triangle, axis=0)
                plt.text(centroid[0], centroid[1], str(ii + 1), fontsize=12)
                plt.gca().add_patch(plt.Polygon(new_triangle, closed=True, facecolor='none',
                                                edgecolor='red', linewidth=2))
                m.append((new_triangle, (beta, gamma, alpha), np.pi-beta-phi))

            triangle_list.append(m)

    # Finding y_max to plot trajectory lines
    y_max = 0
    for m in triangle_list:
        for triangle, _, _ in m:
            y_max = max(y_max, max(triangle[:,1]))

    # Plotting trajectory lines
    x_interval = np.linspace(0, x, 10)
    for b in x_interval:
        y = np.linspace(0, y_max)
        x = (y + np.tan(phi0) * b) / np.tan(phi0)
        plt.plot(x, y, color = "blue")
    plt.axis('scaled')
    plt.show()
if __name__ == "__main__":
    #print(obtain_angles_period())
    evolution(45 * np.pi / 180, 45 * np.pi / 180, np.pi / 2, np.pi / 3,  12)
