import joblib
import pandas as pd

class RandomForestClassifier:
    def __init__(self):
        path_to_artifacts = "/home/patrick/Github/DDOS Detection with Machine Learning/DDOS_Detection/Algorithm Training/"
        self.values_fill_missing =  joblib.load(path_to_artifacts + "train_mode.joblib")
        self.model = joblib.load(path_to_artifacts + "random_forest.joblib")

    def preprocessing(self, input_data):
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0])
        # fill missing values
        input_data.fillna(self.values_fill_missing)
        
        return input_data

    def predict(self, input_data):
        return self.model.predict_proba(input_data)

    def postprocessing(self, input_data):
        label = "BENIGN"
        if input_data[1] > 0.5:
            label = "DDOS"
        return {"probability": input_data[1], "label": label, "status": "OK"}

    def compute_prediction(self, input_data):
        try:
            input_data = self.preprocessing(input_data)
            print("Input data: ", input_data)
            prediction = self.predict(input_data)[0]  # only one sample
            print("Prediction pre processing: ", prediction)
            prediction = self.postprocessing(prediction)
            print("Prediction post processing: ", prediction)
        except Exception as e:
            return {"status": "Error", "message": str(e)}

        return prediction