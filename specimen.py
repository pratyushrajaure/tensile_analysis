from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class Specimen:
    test_id: str
    material: str
    area_mm2: float
    gauge_length_mm: float


class TensileTest:

    def __init__(self, specimen, csv_path):
        self.specimen = specimen
        self.csv_path = csv_path

        self.data = pd.read_csv(csv_path)

        self.clean_data()

    def clean_data(self):

        if "displacement_m" in self.data.columns:
            self.data["displacement_mm"] = (
                self.data["displacement_m"] * 1000
            )

        elif "displacement_mm" in self.data.columns:
            self.data["displacement_mm"] = self.data["displacement_mm"]

        else:
            raise ValueError("Displacement column not found")

        if "force_N" not in self.data.columns:
            raise ValueError("Force column not found")

        # I am keeping only the required columns
        self.data = self.data[["displacement_mm", "force_N"]].copy()

        self.data["displacement_mm"] = pd.to_numeric(
            self.data["displacement_mm"], errors="coerce"
        )

        self.data["force_N"] = pd.to_numeric(
            self.data["force_N"], errors="coerce"
        )

        # Removing missing and duplicate rows
        self.data = self.data.dropna()
        self.data = self.data.drop_duplicates()

        # Removing infinite values
        self.data = self.data.replace([np.inf, -np.inf], np.nan)
        self.data = self.data.dropna()

        # Sorting data by displacement
        self.data = self.data.sort_values("displacement_mm")

        # Removing initial slack
        maximum_force = self.data["force_N"].max()
        threshold = max(5, 0.01 * maximum_force)

        loaded_data = self.data[self.data["force_N"] > threshold].copy()

        if len(loaded_data) > 0:
            self.data = loaded_data

        # Making displacement start from zero
        first_displacement = self.data["displacement_mm"].iloc[0]

        self.data["displacement_mm"] = (
            self.data["displacement_mm"] - first_displacement
        )

        # Calculating stress and strain
        self.data["stress_MPa"] = (
            self.data["force_N"] / self.specimen.area_mm2
        )

        self.data["strain"] = (
            self.data["displacement_mm"] /
            self.specimen.gauge_length_mm
        )

        self.data = self.data.reset_index(drop=True)

    def calculate_youngs_modulus(self):

        # Selecting the initial elastic region
        elastic_data = self.data[
            (self.data["strain"] >= 0.0002) &
            (self.data["strain"] <= 0.002)
        ]

        # Using an early portion if there are too few points
        if len(elastic_data) < 5:
            number_of_points = max(5, int(len(self.data) * 0.15))
            elastic_data = self.data.head(number_of_points)

        strain = elastic_data["strain"]
        stress = elastic_data["stress_MPa"]

        # Fittong a straight line: stress = E*strain+intercept
        slope, intercept = np.polyfit(strain, stress, 1)

        self.youngs_modulus_MPa = slope
        self.youngs_modulus_GPa = slope / 1000

        return self.youngs_modulus_GPa


    def calculate_yield_strength(self):

        if not hasattr(self, "youngs_modulus_MPa"):
            self.calculate_youngs_modulus()

        E = self.youngs_modulus_MPa

        # Calculating the 0.2% offset line
        self.data["offset_stress"] = E * (
            self.data["strain"]-0.002
        )

        # Difference between actual stress and offset line
        difference = (
            self.data["stress_MPa"] - self.data["offset_stress"]
        )

        # Finding where the actual curve crosses from above the offset line to below it
        crossing_points = np.where(
            (difference.iloc[:-1].values >= 0) &
            (difference.iloc[1:].values <= 0)
        )[0]

        # Ignorring the crossings before 0.2% strain
        crossing_points = [
            i for i in crossing_points
            if self.data["strain"].iloc[i] >= 0.002
        ]

        if len(crossing_points) == 0:
            return np.nan

        index = crossing_points[0]

        # Interpolating between the two points
        x1 = self.data["strain"].iloc[index]
        x2 = self.data["strain"].iloc[index + 1]

        y1 = self.data["stress_MPa"].iloc[index]
        y2 = self.data["stress_MPa"].iloc[index + 1]

        d1 = difference.iloc[index]
        d2 = difference.iloc[index + 1]

        if d2 == d1:
            return y1

        fraction = -d1 / (d2 - d1)

        yield_strength = y1 + fraction * (y2 - y1)

        return yield_strength

    def is_complete(self):

        # Checking whether the test shows a significant drop after peak force
        force = self.data["force_N"]

        peak_index = force.idxmax()
        peak_force = force.max()

        after_peak = force.iloc[peak_index + 1:]

        if len(after_peak) < 5:
            return False

        if after_peak.min() < 0.7 * peak_force:
            return True

        return False

    def calculate_uts(self):

        if not self.is_complete():
            return np.nan

        return self.data["stress_MPa"].max()

    def calculate_fracture_strain(self):

        if not self.is_complete():
            return np.nan

        return self.data["strain"].iloc[-1]

    def get_results(self):

        youngs_modulus = self.calculate_youngs_modulus()
        yield_strength = self.calculate_yield_strength()
        uts = self.calculate_uts()
        fracture_strain = self.calculate_fracture_strain()
        complete = self.is_complete()

        return {
            "test_id": self.specimen.test_id,
            "material": self.specimen.material,
            "E_GPa": youngs_modulus,
            "yield_MPa": yield_strength,
            "uts_MPa": uts,
            "fracture_strain": fracture_strain,
            "complete": complete
        }
