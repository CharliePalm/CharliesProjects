import random
import math
class smallSample:
    mean = 0
    sd = 0
    n = 0
    max = 0
    set = []
    min = 0


    def __init__(self, n, min, max, mean, sd):
        self.mean = mean
        self.sd = sd
        self.n = n
        self.max = max
        self.min = min
        self.set = self.dataGen()
        self.recursive()


    def dataGen(self):
        dataset = []
        if self.max < self.min:
            print("hey thats not a max and min")
            return
        for i in range(self.n + 1):
            dataset.append(random.randint(self.min, self.max))
        dataset[0] = self.min
        dataset[self.n - 1] = self.max
        return dataset


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


    def recursive(self):
        mean = self.meanCalc()
        sd = self.sdCalc()
        if (math.isclose(mean, self.mean)
            and math.isclose(sd, self.sd)):
            return self.set

        self.set.sort()

        multiplier = (self.sd / self.sdCalc())
        adder = self.mean - self.meanCalc()

        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] * multiplier

        adder = self.mean - self.meanCalc()

        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] + adder

        if self.set[0] < self.min:
            val = self.set[0]
            for i in range(self.n):
                self.set[i - 1] = self.set[i - 1] * (self.min / val)
        if self.set[self.n - 1] > self.max:
            for i in range(self.n):
                self.set[i - 1] = self.set[i - 1] * (self.max / (self.set[self.n - 1]))
        self.recursive()



##TODO: finish relation to a normal population
class normalPop:
    mean = 0
    sd = 0
    n = 0
    max = 0
    set = []
    min = 0

    def __init__(self, n, min, max, mean, sd):
        self.mean = mean
        self.sd = sd
        self.n = n
        self.max = max
        self.min = min
        self.set = self.dataGen()
        self.recursive()

    def dataGen(self):
        dataset = []
        if self.max < self.min:
            print("hey thats not a max and min")
            return
        for i in range(self.n + 1):
            dataset.append(random.randint(self.min, self.max))
        dataset[0] = self.min
        dataset[self.n - 1] = self.max
        return dataset


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


    def recursive(self):
        mean = self.meanCalc()
        sd = self.sdCalc()
        self.set.sort()
        iqr = self.set[int((3 * self.n) / 4)] - self.set[int(self.n / 4)]
        iqrCalc = int((mean + .6745 * sd) - (mean - .6745 * sd))

        if (math.isclose(mean, self.mean)
            and math.isclose(sd, self.sd)
            and iqr == iqrCalc):
            return self.set
        elif (math.isclose(mean, self.mean)
            and math.isclose(sd, self.sd)):

            for i in range(1, int(self.n / 4)):
                self.set[i - 1] = self.set[i - 1] * 1.5
            for i in range(int((3 * self.n) / 4), self.n):
                self.set[i] = self.set[i - 1] * .99
            self.recursive()


        multiplier = (self.sd / self.sdCalc())
        adder = self.mean - self.meanCalc()

        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] * multiplier

        adder = self.mean - self.meanCalc()

        for i in range(len(self.set)):
            self.set[i - 1] = self.set[i - 1] + adder

        self.set[0] = self.min
        self.set[len(self.set) - 1] = self.max
        print(self.set)
        self.recursive()

if __name__ == '__main__':
    ##insert test values here, possible integration with other platforms here
    set = smallSample(50, 1, 10, 5, 3)
    print(set.set)
