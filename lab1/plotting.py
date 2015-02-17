import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *
import matplotlib.patches as mpatches

# Class that parses a file and plots several graphs
class Plotter:
    def __init__(self):
        # create some fake data
        self.x = []
        self.y = []
        self.all = []
        # x ranges from 0 to 9
        for i in range(0,10):
            self.x.append(i)
            vals = []
            # each x value has 100 random values of X + random(0,10)
            for j in range(0,100):
                val = i + 10*random()
                vals.append(val)
                # keep track of all values ever generated
                self.all.append(val)
            self.y.append(vals)
        # keep track of the averages for each X
        self.averages = []
        for array in self.y:
            self.averages.append(average(array))

    def equationPlot(self):
        """ Create a line graph of an equation. """
        clf()
        x = np.arange(0,9.9,0.1)
        plot(x,1/(10-x))
        xlabel('X')
        ylabel('1/(10-x)')
        savefig('equation.png')

    def linePlot(self):
        """ Create a line graph. """
        clf()
        plot(self.x,self.averages)
        xlabel('X Label (units)')
        ylabel('Y Label (units)')
        savefig('line.png')

    def linePlotData(self,xdata, ydata, xname, yname):
        """ Create a line graph. """
        clf()

        #theoretical
        rho = np.arange(0,1,1.0/100)
        mu = 1000000.0 / (1000.0 * 8.0)
        plot(rho,(1/(2*mu))*(rho/(1-rho)),label='Theory',color="green")

        #actual
        plot(xdata, ydata,label="Average",color="blue")

        legend(loc='upper left')

        #theoretical
        xlabel(xname)
        ylabel(yname)
        savefig('line.png')

    def boxPlot(self):
        """ Create a box plot. """
        clf()
        boxplot(self.y,positions=self.x,widths=0.5)
        xlabel('X Label (units)')
        ylabel('Y Label (units)')
        savefig('boxplot.png')

    def combinedPlot(self):
        """ Create a graph that includes a line plot and a boxplot. """
        clf()
        # plot the line
        plot(self.x,self.averages)
        # plot the boxplot
        boxplot(self.y,positions=self.x,widths=0.5)
        xlabel('X Label (units)')
        ylabel('Y Label (units)')
        savefig('combined.png')

    def histogramPlot(self):
        """ Create a histogram. """
        clf()
        hist(self.all,bins=range(0,20),rwidth=0.8)
        savefig('histogram.png')

if __name__ == '__main__':
    p = Plotter()
    p.equationPlot()
    p.linePlot()
    p.boxPlot()
    p.combinedPlot()
    p.histogramPlot()