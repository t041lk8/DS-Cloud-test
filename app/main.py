from kserve import ModelServer

from model import MyModel


if __name__ == "__main__":
    model = MyModel("NERtagger")
    model.load()
    ModelServer().start([model])