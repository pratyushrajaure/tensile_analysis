
from pathlib import Path
import pandas as pd

from specimen import Specimen, TensileTest


class TestCampaign:

    def __init__(self, data_folder):

        self.data_folder = Path(data_folder)

        self.raw_folder = self.data_folder / "raw"
        self.specimens_file = self.data_folder / "specimens.csv"

        self.tests = []
        self.errors = []

        self.load_tests()

    def load_tests(self):

        specimens = pd.read_csv(self.specimens_file)

        for index, row in specimens.iterrows():

            test_id = str(row["test_id"])

            try:
                specimen = Specimen(
                    test_id=test_id,
                    material=row["material"],
                    area_mm2=row["area_mm2"],
                    gauge_length_mm=row["gauge_length_mm"]
                )

                csv_path = self.raw_folder / f"{test_id}.csv"

                test = TensileTest(specimen, csv_path)

                self.tests.append(test)

            except Exception as error:

                message = f"{test_id}: {error}"
                self.errors.append(message)

                print("Error:", message)

    def get_summary(self):

        results = []

        for test in self.tests:

            try:
                result = test.get_results()
                results.append(result)

            except Exception as error:

                print(
                    f"Error processing {test.specimen.test_id}: {error}"
                )

        summary = pd.DataFrame(results)

        return summary

    def save_summary(self, output_folder):

        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        summary = self.get_summary()

        summary.to_csv(
            output_folder / "summary.csv",
            index=False
        )

        return summary
