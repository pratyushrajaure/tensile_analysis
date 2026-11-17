
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from campaign import TestCampaign


BASE_FOLDER = Path(__file__).parent

DATA_FOLDER = BASE_FOLDER / "data"
OUTPUT_FOLDER = BASE_FOLDER / "outputs"


def plot_force_displacement(campaign):

    selected_tests = campaign.tests[:2]

    for test in selected_tests:

        plt.figure(figsize=(8, 5))

        plt.plot(
            test.data["displacement_mm"],
            test.data["force_N"],
            label=test.specimen.test_id
        )

        plt.xlabel("Displacement (mm)")
        plt.ylabel("Force (N)")
        plt.title(
            f"Force vs Displacement - {test.specimen.test_id}"
        )

        plt.legend()
        plt.grid(True)

        filename = (
            f"force_displacement_{test.specimen.test_id}.png"
        )

        plt.savefig(OUTPUT_FOLDER / filename, dpi=300)
        plt.close()


def plot_stress_strain(campaign):

    materials = sorted(set(
        test.specimen.material for test in campaign.tests
    ))

    for material in materials:

        plt.figure(figsize=(9, 6))

        material_tests = [
            test for test in campaign.tests
            if test.specimen.material == material
        ]

        for test in material_tests:

            test.calculate_youngs_modulus()

            yield_strength = test.calculate_yield_strength()

            plt.plot(
                test.data["strain"],
                test.data["stress_MPa"],
                label=test.specimen.test_id
            )

            if pd.notna(yield_strength):

                index = (
                    test.data["stress_MPa"] - yield_strength
                ).abs().idxmin()

                plt.scatter(
                    test.data["strain"].iloc[index],
                    test.data["stress_MPa"].iloc[index],
                    marker="o"
                )

            if test.is_complete():

                index = test.data["stress_MPa"].idxmax()

                plt.scatter(
                    test.data["strain"].iloc[index],
                    test.data["stress_MPa"].iloc[index],
                    marker="x"
                )

        plt.xlabel("Engineering Strain")
        plt.ylabel("Engineering Stress (MPa)")
        plt.title(f"Stress-Strain Curves - {material}")

        plt.legend()
        plt.grid(True)

        filename = f"stress_strain_{material}.png"

        plt.savefig(OUTPUT_FOLDER / filename, dpi=300)
        plt.close()


def plot_yield_boxplot(summary):

    valid_data = summary.dropna(subset=["yield_MPa"])

    if valid_data.empty:

        print(
            "Yield strength boxplot skipped: "
            "no valid yield values were calculated."
        )

        return

    plt.figure(figsize=(8, 5))

    materials = sorted(valid_data["material"].unique())

    values = []

    for material in materials:

        material_values = valid_data[
            valid_data["material"] == material
        ]["yield_MPa"]

        values.append(material_values)

    plt.boxplot(
        values,
        tick_labels=materials
    )

    plt.xlabel("Material")
    plt.ylabel("Yield Strength (MPa)")
    plt.title("Yield Strength Comparison")

    plt.grid(axis="y")

    plt.savefig(
        OUTPUT_FOLDER / "yield_strength_boxplot.png",
        dpi=300
    )

    plt.close()


def main():

    print("Starting tensile test analysis...")

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    campaign = TestCampaign(DATA_FOLDER)

    summary = campaign.save_summary(OUTPUT_FOLDER)

    print("\nSummary saved successfully.")
    print("\nTest summary:")
    print(summary)

    print("\nAverage mechanical properties by material:")

    averages = summary.groupby("material")[
        ["E_GPa", "yield_MPa", "uts_MPa"]
    ].mean()

    print(averages)

    incomplete_tests = summary[
        summary["complete"] == False
    ]

    print("\nIncomplete tests:")

    if len(incomplete_tests) > 0:
        print(incomplete_tests["test_id"].to_list())
    else:
        print("No incomplete tests detected.")

    print("\nGenerating graphs...")

    plot_force_displacement(campaign)

    plot_stress_strain(campaign)

    plot_yield_boxplot(summary)

    print("Graphs saved in the outputs folder.")

    if campaign.errors:

        print("\nFiles that could not be loaded:")

        for error in campaign.errors:
            print(error)

    print("\nAnalysis finished.")


if __name__ == "__main__":
    main()
