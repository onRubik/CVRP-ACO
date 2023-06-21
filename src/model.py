# from controller import Controller
from data_integrity import DataIntegrity


class Model:
    def __init__(self, csv_to_db: str):
        self.csv_to_db = csv_to_db


    def csvIntoDb(self):
        