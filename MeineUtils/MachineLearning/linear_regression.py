import numpy as np
import matplotlib.pyplot as plt

from MeineUtils.General import flatten_list

class LinearRegression():
    def __init__(self, file_path, epochs=50, minibatch_size=20, learning_rate = 0.001, data_shuffle=False, delimiter=',', skip_header=1, loss_function=(lambda y_hat, y: (y_hat-y)**2), stochastic=False):
        self.file_path = file_path
        self.epochs = epochs
        self.minibatch_size = minibatch_size
        self.learning_rate = learning_rate
        self.data_shuffle = data_shuffle
        self.loss_function = loss_function

        self.stochastic = stochastic
        if self.stochastic and self.data_shuffle:
        # if self.stochastic and not self.data_shuffle: 
            print(f'data_shuffle: {self.data_shuffle} => False')
            self.data_shuffle = False
            # print(f'data_shuffle: {self.data_shuffle} => True')
            # self.data_shuffle = True

        if '.csv' in self.file_path:
            self.from_csv(file_path=self.file_path, delimiter=delimiter, skip_header=skip_header)

        self.thetas = np.random.randn(self.X.shape[1]+1, 1)
        self.thetas_all = [self.thetas]  

        self.losses_all = [] 
    
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

    def predict(self, x):
        if not isinstance(x, np.ndarray):
            if not isinstance(x, list):
                x = [x]
            x = np.array(x)
        if len(x) == self.X.shape[1]:
            x = np.insert(arr=x, obj=0, values=1.0)
        return x.dot(self.thetas)

    def main(self):
        for _ in range(self.epochs):
            if self.data_shuffle:
                shuffled_indices = np.random.permutation(self.max_feature)
                X_b_shuffled = self.X_b[shuffled_indices]
                y_shuffled = self.y[shuffled_indices]
            else:
                X_b_shuffled = self.X_b
                y_shuffled = self.y

            _loss = []
            for i in range(0, self.max_feature, self.minibatch_size):
                if self.stochastic:
                    # random_index = np.random.randint(np.maximum(self.max_feature-self.minibatch_size, 1))
                    # xi = X_b_shuffled[random_index:random_index+self.minibatch_size]
                    # yi = y_shuffled[random_index:random_index+self.minibatch_size]
                    random_index = np.random.randint(self.max_feature)
                    xi = X_b_shuffled[random_index:random_index+1]
                    yi = y_shuffled[random_index:random_index+1]
                else:
                    xi = X_b_shuffled[i:i+self.minibatch_size]
                    yi = y_shuffled[i:i+self.minibatch_size]
                
                # compute output 
                output = self.predict(xi)
                
                # loss
                loss = self.loss_function(output, yi)
                
                # derivative of loss
                loss_grd = 2*(output - yi)/self.minibatch_size
                
                # derivative of parameters
                gradients = xi.T.dot(loss_grd)
                
                # update thetas
                self.thetas = self.thetas - self.learning_rate*gradients
                self.thetas_all.append(self.thetas)
                
                # loss mean
                loss_mean = np.sum(loss)/self.minibatch_size
                _loss.append(loss_mean)
            self.losses_all.append(_loss)
        return self
    
    def plot(self, color="r", data_range=500):
        losses_list = flatten_list(self.losses_all)
        if data_range > len(losses_list):
            print(f'data_range: {data_range} => {len(losses_list)}')
            data_range = len(losses_list)
        plt.plot(list(range(data_range)), flatten_list(self.losses_all)[:data_range], color=color)
        plt.show()
        return self