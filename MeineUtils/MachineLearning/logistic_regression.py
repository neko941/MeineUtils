import numpy as np
import matplotlib.pyplot as plt

from MeineUtils.General import flatten_list

class LogisticRegression():
    def __init__(self, 
                 file_path, 
                 delimiter=',', 
                 skip_header=1, 
                 minibatch_size=32,
                 epochs=100,
                 learning_rate = 0.01,
                 data_shuffle=True,
                 thetas=None,
                 loss_function=(lambda y_hat, y: (-y * np.log(y_hat) - (1 - y) * np.log(1 - y_hat)).mean())):
        self.file_path = file_path
        self.minibatch_size = minibatch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.data_shuffle = data_shuffle
        self.loss_function = loss_function
        if '.csv' in self.file_path:
            self.from_csv(file_path=self.file_path, delimiter=delimiter, skip_header=skip_header)

        if thetas:
            thetas = flatten_list(thetas)
            while(len(thetas) < self.X.shape[1]+1): thetas.append(np.random.randn())
            while(len(thetas) > self.X.shape[1]+1): thetas.pop()
            self.thetas = np.array(thetas).reshape(self.X.shape[1]+1, 1)
        else:
            self.thetas = np.random.randn(self.X.shape[1]+1, 1)

        self.thetas_all = [self.thetas]
        self.losses_all = []
        self.accuracy_all = []
    
    def from_csv(self, file_path, delimiter=',', skip_header=1):
        self.data = np.genfromtxt(file_path,  delimiter=delimiter, skip_header=skip_header)
        self.max_feature = self.data.shape[0]
        if self.minibatch_size == 'all' or self.minibatch_size > self.max_feature:
            print(f'minibatch_size: {self.minibatch_size} => {self.max_feature}')
            self.minibatch_size = self.max_feature
        self.X = self.data[:,:-1]
        self.y = self.data[:,-1:]
        self.X_b = np.concatenate((np.ones((self.max_feature, 1)), self.X), axis=1)
        return self

    def sigmoid_function(self, z):
        return 1 / (1 + np.exp(-z))

    def predict(self, x):    
        return self.sigmoid_function(x.dot(self.thetas))

    def main(self):
        for _ in range(self.epochs):
            if self.data_shuffle:
                shuffled_indices = np.random.permutation(self.max_feature)
                X_b_shuffled     = self.X_b[shuffled_indices]
                y_shuffled       = self.y[shuffled_indices]
            else:
                X_b_shuffled = self.X_b
                y_shuffled = self.y

            _loss = []
            _acc = []
            for i in range(0, self.max_feature, self.minibatch_size):
                xi = X_b_shuffled[i:i+self.minibatch_size]
                yi = y_shuffled[i:i+self.minibatch_size]
            
                # compute output
                output = self.predict(xi)

                # compute loss
                loss = self.loss_function(output, yi)

                # compute gradient
                gradient = np.dot(xi.T, (output - yi)) / self.minibatch_size

                # update
                self.thetas -= self.learning_rate*gradient 
                self.thetas_all.append(self.thetas)

                # loss
                _loss.append(loss)

                # accuracy
                preds = self.predict(xi).round()
                acc = (preds == yi).mean()
                _acc.append(acc)
            self.losses_all.append(_loss)
            self.accuracy_all.append(_acc)
        return self

    def plot(self, color="r", data_range=400):
        losses_list = flatten_list(self.losses_all)
        if data_range > len(losses_list):
            print(f'data_range: {data_range} => {len(losses_list)}')
            data_range = len(losses_list)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(flatten_list(self.accuracy_all), color="#1abd15", linewidth=3, label='accuracy')
        ax.plot(losses_list, color="#d35400", linewidth=3, label='losses')
        ax.legend()
        fig.show()
        return self