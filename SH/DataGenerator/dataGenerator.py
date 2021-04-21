import random
import math
import numpy as np
import matplotlib.pyplot as plt

class DataGen:
    def __init__(self, n, min, max, mean, sd):
        self.mean = mean
        self.sd = sd
        self.n = n
        self.max = max
        self.min = min

    def sdCalc(self):
        sum = 0.0
        a = self.meanCalc()
        for i in self.set:
            sum = sum + (i-a) ** 2
        return (sum / (len(self.set) - 1)) ** .5

    def meanCalc(self):
        sum = 0.0
        for i in self.set:
            sum = sum + i
        return sum / len(self.set)

## small sample is a way of estimating data from a random point of view
## this method is far more unpredictable and often has outliers, akin to a
## small sample population.
class smallSample(DataGen):
    mean = 0
    sd = 0
    n = 0
    max = 0
    set = []
    min = 0


    def __init__(self, n, min, max, mean, sd):
        super().__init__(n, min, max, mean, sd)
        self.set = self.dataGen()
        self.recursive()


    def dataGen(self):
        dataset = []
        if self.max < self.min:
            print("hey thats not a max and min!")
            return
        for i in range(self.n + 1):
            dataset.append(random.randint(self.min, self.max))

        dataset[0] = self.min
        dataset[self.n - 1] = self.max
        return dataset


    def sdCalc(self):
        super().sdCalc()


    def meanCalc(self):
        super().meanCalc()

    def recursive(self):
        mean = self.meanCalc()
        sd = self.sdCalc()
        ## start by checking exit clause
        if (math.isclose(mean, self.mean)
            and math.isclose(sd, self.sd)):
            return self.set
        # ensure set is sorted
        self.set.sort()

        # now we need to shift the SD and the mean
        multiplier = (self.sd / self.sdCalc())

        #Update values according to shift
        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] * multiplier

        adder = self.mean - self.meanCalc()

        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] + adder

        # reset the values if the bounds have been broken
        if self.set[0] < self.min:
            val = self.set[0]
            for i in range(self.n):
                self.set[i - 1] = self.set[i - 1] * (self.min / val)
        if self.set[self.n - 1] > self.max:
            for i in range(self.n):
                self.set[i - 1] = self.set[i - 1] * (self.max / (self.set[self.n - 1]))

        #iterate again
        self.recursive()

# this class generates data very rigidly: there is a set distance between data values that shifts
# as frequency increases. It will always create the same data when passed the same values. Thereby it's
# better to pass high values of n into the init

class normalPopulation(DataGen):
    mean = 0
    sd = 0
    n = 0
    max = 0
    set = []
    min = 0

    def __init__(self, n, min, max, mean, sd):
        super().__init__(n, min, max, mean, sd)
        self.set = self.dataGen()


    # since we're generating normal data, we can rely on the probability density function,
    # and thereby, the Irwin-Hall distribution. You can read more here:
    #https://en.wikipedia.org/wiki/Irwin%E2%80%93Hall_distribution#:~:text=In%20probability%20and%20statistics%2C%20the,each%20having%20a%20uniform%20distribution.
    def dataGen(self):
        dataset = []
        val = self.min
        if self.max < self.min:
            print("hey thats not a max and min")
            return

        for i in range(self.n):
            sum = 0
            ## sample 12 times from the uniform distribution
            for i in range(12):
                sum += random.random()
            sum -= 6
            dataset.append(sum)

        for i in range(len(dataset)):
            dataset[i] *= self.sd
            dataset[i] += self.mean

        self.recursiveFix()

        return dataset


    def recursiveFix(self):
        #TODO: add fix for max and in
        return

    def sdCalc(self):
        return super().sdCalc()


    def meanCalc(self):
        return super().meanCalc()

if __name__ == '__main__':
    ##TODO: add user interface and interaction
    set = normalPopulation(100000, 1, 10, 5, 3)
    print(set.sdCalc())
    y = []
    for i in range(200):
        y.append(i)
    set.set.sort()
    plt.hist(set.set, bins=50)
    plt.show()
