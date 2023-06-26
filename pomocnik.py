import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(wynik, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Nauczanie...')
    plt.xlabel('Numer gier')
    plt.ylabel('Wynik')
    plt.plot(wynik)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(wynik)-1, wynik[-1], str(wynik[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    plt.pause(.1)