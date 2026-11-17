# Tensile Test Analysis



A Python project for analysing tensile test data of different materials: steel, aluminium, and copper.



## Project Structure



```text

tensile_analysis/

│

├── main.py

├── specimen.py

├── campaign.py

├── README.md

│

├── data/

│   ├── specimens.csv

│   └── raw/

│

└── outputs/

&#x20;   ├── summary.csv

&#x20;   └── graphs/

```



## Requirements



Install the required Python libraries:



```bash

pip install numpy pandas matplotlib

```



## How to Run



1. Place the specimen information in `data/specimens.csv`.

2. Place the raw tensile test CSV files inside `data/raw/`.

3. Open the project folder in your terminal.

4. Run:



```bash

python main.py

```



## Project Files



- **main.py:** Runs the complete analysis and generates graphs.

- **specimen.py:** Defines specimen and tensile test classes, including data cleaning and mechanical property calculations.

- **campaign.py:** Manages multiple tensile tests and generates the summary table.



## Outputs



The program generates:



- `summary.csv` – Calculated mechanical properties for each test.

- Force vs displacement graphs.

- Stress vs strain curves for each material.

- Yield strength comparison box plot.



## Mechanical Properties



The project calculates:



- Young's Modulus (GPa)

- Yield Strength (MPa) using the 0.2% offset method

- Ultimate Tensile Strength (MPa)

- Fracture Strain



Incomplete tests are flagged, and their UTS and fracture strain are left empty.



---


