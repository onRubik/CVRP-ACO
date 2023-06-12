from controller import Controller


class mainModel:
    def runModel(self):
        file_name = 'ran1'
        n = 25
        multiplier = 200
        newController = Controller(file_name, n, multiplier)
        newController.createRandomPoints()
        pass


if __name__ == '__main__':
    newMainModel = mainModel()
    newMainModel.runModel()