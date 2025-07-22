# Demand Flexibility Controls Library using Semantics (DFLEXLIBS)

**DFLEXLIBS** is a Python library for developing and deploying **HVAC-based demand flexibility control applications**. It focuses on **portable** control applications that exclusively contain control logic and are abstract to specific building implementations, such as point names and communication protocols.

The library uses **semantic models** and **control platform-oriented interfaces** to configure and run controls in real or virtual buildings.


## Features

- 🛠️ **Control Applications**  
  Available controls are based on the [Open DF Control Sequence Specification](https://doi.org/10.1016/j.enbuild.2025.115616)

- 📊 **Analytics Applications (to evaluate controls performance and variability)**  
  Available analytics are based on the [Annex 81 Energy Flexibility KPIs Python Package](https://github.com/HichamJohra/energy_flexibility_kpis)


## Tested Control Platforms

DFLEXLIBS has been tested on:

- 🏢 Four **virtual buildings** via [BOPTEST](https://github.com/ibpsa/project1-boptest/tree/master)  
- 🏠 Three **real buildings** via [VOLTTRON](https://volttron.readthedocs.io/en/main/)


## Getting Started 

To access the library, follow these steps:

1. Clone the repository
   ``` 
   git clone https://github.com/LBNL-ETA/DFLEXLIBS.git 
   ```

2. Install the library and dependencies

   Install the controls library using the development mode. Run the following command:

   ```
   python setup.py develop
   ```

   Install the required dependencies by using the `requirements.txt file`. Run the following command:

   ```
   pip install -r requirements.txt
   ``` 

   Create a virtual environment with the controls package and other required dependencies using `pipenv`. Run the following command:

   ``` 
   pipenv install --dev
   ```

3. (For the analytics scritp) Initialize and update the library's submodules from `energy_flexibility_kpis repo`

   ``` 
   git submodule update --init --recursive
   ```
   
## Validating BOPTEST Examples

To run BOPTEST examples, follow these steps:

1. Open the `_examples/boptest/validation` directory.

2. Run the validation

   Open `control_validation.ipynb` module, select a testcase and run the code. Check all valid controls for that test.

## Running BOPTEST Examples

1. Open the `_examples/boptest` directory.

2. Run the simulation

   Select a testcase and a control application that is suitable for the test case and run the `simulation.ipynb` module. It will first run the test case baseline control and generate datasets (csv). Then it will run the proposed DF control application and generate datasets (csv). You can see the datasets and generate plots of the tested applications in the `results` directories for each test case. 

## Calculating KPIs 

1. Open the `_analytics` directory.

2. Run the analytic apps

   Open `kpis_calculation.ipynb` module, select a testcase and control, run the code. 

3. Check the results

   Open the `_analytics/results` directory and check the results from each test case for each control application.
   Individual analytic results is saved within each testcase directory for each control. 

## Contributing

If you are interested in contributing to the library:

- You are welcome to report any issues in [Issues](https://github.com/LBNL-ETA/DFLEXLIBS/issues).
- You are also welcome to follow the [Contribution Guide](https://github.com/LBNL-ETA/DFLEXLIBS/edit/main/doc) for:
   - Creating new control functions and applications
   - Running the control applications reusing the available interfaces (BOPTEST and VOLTTRON)
   - Creating new interfaces to run the applications in other control platforms/environments

## Copyright Notice

Demand Flexibility Controls Library using Semantics (DFLEXLIBS) 
Copyright (c) 2023, The Regents of the University of California,
through Lawrence Berkeley National Laboratory (subject to receipt of
any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative 
works, and perform publicly and display publicly, and to permit others to do so.


## License

DFLEXLIBS is available under the following open-source [license](https://github.com/LBNL-ETA/DFLEXLIBS/edit/main/License.txt).


## Related Publications

de Andrade Pereira, Flavia; Paul, Lazlo; Pritoni, Marco; Casillas, Armando; Prakash, Anand; Huang, Weiping; Shaw, Conor;  Martín-Toral, Susana; Finn, Donal; O’Donnell, James.
Enabling portable demand flexibility control applications in virtual and real buildings, Journal of Building Engineering,
Volume 86, 2024. https://doi.org/10.1016/j.jobe.2024.108645.

Paul, Lazlo; De Andrade Pereira, Flavia; Prakash, Anand; Ham, Sang woo; Brown, Rich; Feng, Jingjuan Dove; Pritoni, Marco. Open Building Operating System: a Grid-Responsive Semantics-Driven Control Platform for Buildings. Science and Technology for the Built Environment, 2024. https://doi.org/10.1080/23744731.2024.2444819

Paul, Lazlo; De Andrade Pereira, Flavia; Ham, Sang woo;Pritoni, Marco; Brown, Rich; Feng, Jingjuan Dove. Open Building Operating System: an Open-Source Grid Responsive Control Platform for Buildings (2023). ASHRAE Annual Conference 2023.

de Andrade Pereira, Flavia; Pritoni, Marco; Martín-Toral, Susana; Finn, Donal; O’Donnell, James. A semantics-driven framework for scalable demand flexibility control applications (2023). Proceedings of the 2023 European Conference on Computing in Construction and the 40th International CIB W78 Conference.
http://www.doi.org/10.35490/EC3.2023.341


