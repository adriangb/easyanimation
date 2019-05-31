# Imports
import numpy as np
from Libraries.ListBuffer import ListBuffer
from Libraries.AnimatedFigure import AnimatedFigure

counter = float(0)


def get_samples(n_pts=1):
    global counter
    new_t, new_cos, new_sin, new_sin2, new_cos2 = np.zeros((5, n_pts))
    for i in range(n_pts):
        new_t[i] = counter
        new_cos[i] = np.cos(counter)
        new_sin[i] = np.sin(counter)
        new_sin2[i] = np.sin(counter) ** 2
        new_cos2[i] = np.cos(counter) ** 2
        counter = counter + .1
    return [new_t, new_cos, new_sin, new_sin2, new_cos2]


# Must return a list of tuples for every desired plot
def update_function(i):
    global t, cos, sin, sin2, cos2
    new_data = get_samples(n_pts=1)
    t.add(new_data[0])
    cos.add(new_data[1])
    sin.add(new_data[2])
    sin2.add(new_data[3])
    cos2.add(new_data[1])
    return [(t, cos, sin2), (t, sin), (t, sin2), (t, cos2)]


# create empty buffers to store data as a list of tuples
n_pts = 400

t = ListBuffer([], maxlen=n_pts)
cos = ListBuffer([], maxlen=n_pts)
sin = ListBuffer([], maxlen=n_pts)
sin2 = ListBuffer([], maxlen=n_pts)
cos2 = ListBuffer([], maxlen=n_pts)

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