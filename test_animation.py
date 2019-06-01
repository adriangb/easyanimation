# Imports
import numpy as np
from collections import deque
from AnimatedFigure import AnimatedFigure


# Must return a list of tuples for every desired plot
def update_function(i):
    t.append(i / 500 * 2 * np.pi)
    cos.append(np.cos(t[-1]))
    sin.append(np.sin(t[-1]))
    sin2.append(np.sin(t[-1]) ** 2)
    cos2.append(np.cos(t[-1]) ** 2)
    return [(t, cos, sin2), (t, sin), (t, sin2), (t, cos2)]


# create empty buffers to store data as a list of tuples
n_pts = 400

t = deque([], maxlen=n_pts)
cos = deque([], maxlen=n_pts)
sin = deque([], maxlen=n_pts)
sin2 = deque([], maxlen=n_pts)
cos2 = deque([], maxlen=n_pts)

buffers = [t, cos, sin, sin2, cos2]

# create animation object
an = AnimatedFigure(update_function, plot_samples=n_pts, interval=1, debug=True)

# label plots
axes = an.axes
axes[0].set_title('cos(t)')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Amplitude')

axes[1].set_title('sin(t)')
axes[1].set_ylabel('Amplitude')
axes[1].set_xlabel('Time (s)')

axes[2].set_title('sin**2(t)')
axes[2].set_ylabel('Amplitude Squared')
axes[2].set_xlabel('Time (s)')

axes[3].set_title('cos**2(t)')
axes[3].set_ylabel('Amplitude Squared')
axes[3].set_xlabel('Time (s)')

# begin animation
an.animate()
