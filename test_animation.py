# Imports
import numpy as np
from collections import deque

# Set library to use
lib = "qt"      # change to "qt" to test that version

if lib == "matplotlib":
    from src.AnimatedFigure import AnimatedFigure
else:
    from src.AnimatedFigureQt import AnimatedFigure


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

an = AnimatedFigure(update_function, plot_samples=n_pts, interval=1)
# create animation object
if lib == "matplotlib":

    # label plots
    axes = an.axes
    axes[0].set_title('Two lines')
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].legend(("cos(t)", "sin2(t)"))

    axes[1].set_title('sin(t)')
    axes[1].set_ylabel('Amplitude')
    axes[1].set_xlabel('Time (s)')

    axes[2].set_title('sin**2(t)')
    axes[2].set_ylabel('Amplitude Squared')
    axes[2].set_xlabel('Time (s)')

    axes[3].set_title('cos**2(t)')
    axes[3].set_ylabel('Amplitude Squared')
    axes[3].set_xlabel('Time (s)')
else:
    # label plots
    axes = an.axes
    plot_items = an.curves
    axes[0].setTitle(title='Two lines')
    axes[0].setLabel(axis='bottom', text='Time (s)')
    axes[0].setLabel(axis='left', text='Amplitude')
    # Workaround to set labels easily. When curves are created, names are set to these values.
    plot_items[0][0] = "cos(t)"
    plot_items[0][1] = "sin2(t)"

    axes[1].setTitle(title='sin(t)')
    axes[1].setLabel(axis='bottom', text='Time (s)')
    axes[1].setLabel(axis='left', text='Amplitude')

    axes[2].setTitle(title='sin**2(t)')
    axes[2].setLabel(axis='bottom', text='Time (s)')
    axes[2].setLabel(axis='left', text='Amplitude')

    axes[3].setTitle(title='cos**2(t)')
    axes[3].setLabel(axis='bottom', text='Time (s)')
    axes[3].setLabel(axis='left', text='Amplitude')

# begin animation
an.animate()
