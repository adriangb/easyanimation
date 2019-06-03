# EasyAnimation
## Wrapper for matplotlib FuncAnimation to simplify axis rescaling, subplots, multiple lines.

## How to use
1. Git clone this repo ```git clone https://github.com/adriangb/easy_animation.git```
2. `cd` to the folder where you cloned it.
3. Run ```pipenv install```
4. Run the test file: ```pipenv run python test_animation.py```

## Background
I noticed that live-plotting data in matplotlib can be done in one of three ways:

1. Using iteration, manually calling commands to re-plot data.
2. Using the matplotlib.animation module _without_ blitting (axis will rescale etc.)
3. Using the matplotlib.animation module _with_ blitting (axis will NOT rescale etc.)

There are pros and cons to each:

1. Is very easy to write and supports dynamic anything (titles, labels, scaling, etc.). This works fine for data at <10Hz, but is incredibly slow and resource intensive for anything above this.
2. This automatically handles timing and some other details, but adds a good amount of complexity. Without blitting, not much speed is gained over the iterative approach. As soon as the animation module is introduced instead of manual redrawing, compatibility with IPython inline plotting is broken, and at least in Spyder the whole kernel crashes on closing plots (I'm guessing some type of loop in which the animation is now calling a dead plot).
3. Here the complexity is greatest and flexibility minimal. For example, if you are live plotting sensor data that varies over a couple orders of magnitude, you would have to hardcode your axis limits and either not see the data or have it cut off. All of the issues present in (2) also apply. However, this method can plot multiple subplots at 100+ fps. Not quite as fast as using Qt directly but a lot more user friendly since the most of the syntax is good old matplotlib.

The goal of this project was to take option (3) and do two things:
1. Reduce the complexity by auto-generating and auto-updating plots based on the signature of the data generating function.
2. Enable basic dynamic axis resizing. This is done by using generous hysterisis thersholds and only allowing resizing every couple frames.

The usage can be seen in test_animation.py. The basic idea is that you create a function that accepts a frame number argument and returns a nested iterable containing the data. Ex:
```python
def update_function(i):
    x1 = list(range(i))
    y11 = x1 * 2
    y12 = x1 ** 2
    x2 = x + 10
    y21 = x2 ** 3
    return [(x1, y11, y22), (x2, y21)]
```

Then, you need to instantiate the animation object. Note that this will call update_function() once in order to determine it's signature and generate plots accordingly. The figure is saved in the animation object, allowing titles, labels, etc. to be set before the animation starts. The required arguments are the update function object as well as the number of samples to plot, which must have the same shape as the signature of the update function _or_ can be a single numeber that is applied to all plots.
```python
an = AnimatedFigure(update_function, plot_samples=(100, 20))
an.axes[0].set_title("First subplot")
```

Finally, you call ```an.animate()``` to start the plotting.

When you close the figure, a ```KeyboardInterrupt``` is raised. This way, you can handle plot closing in the same way you would handle a Ctrl+C (both signify the user is saying stop the current task, move on or quit). You could also quit the live plot by calling an.stop() at some specific frame number or other condition.

For IPython, the backend is auto-switched to TKinter for live plotting and then reset to inline once the live plot is closed.

You'll also notice that the entire figure is redrawn to update the axis. While this does have a performance hit, it isn't large since it should not be happening too often. In order to blit the axis tick labels for the specific axis on the specific subplot that needs to be updated we would have to modify the animation module to correctly get the bbox, which is not trivial for text due to the way it is rendered in matplotlib. Thus, the easier method is to redraw the whole figure.

Okay you made it this far. Maybe you tried this and it was still too slow? Here's an alternative Qt based solution:

In test_animation.py change backend to "qt".

You will need to have the dev build of pyqtgraph. The pipfile should take care of this.
