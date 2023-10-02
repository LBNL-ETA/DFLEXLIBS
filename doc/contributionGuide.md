
### Adding a New Control Function 

To add a new function to the `controls/hvac/sequences/python/functions` directory, follow these steps:

1. Open the `controls/hvac/sequences/python/functions` directory.

2. Add a new function: 

   Create a new module file in the directory and write the code for your new function in the module file. Name the file something descriptive that indicates what the function does.

3. Save the module file in the `controls/hvac/sequences/python/functions` directory.

4. Open the `__init__.py` file in the `controls/hvac/sequences/python/functions` directory.

5. Add module name to the `__all__` list

   Add the name of your new module to the `__all__` list in the `__init__.py` file. This allows other files to import your new module and use the function you just created.

6. Save the `__init__.py` file.

7. For running the new function in the BOPTEST interface. In the `examples/boptest/` directory, open the `BOPTEST_interface` file corresponding to the control strategy that will use your new function.

8. Import your new module at the top of the `BOPTEST_interface` file.

9. Call your function

   Find the `compute_control()` function in the `BOPTEST_interface` file. This is where you will call your new function. Add your new function as a parameter when calling the `compute_control()` function in the interface.

10. Use your function

    In the `controls/hvac/sequences/python/strategies` directory find the control strategy module that corresponds to the `BOPTEST_interface` file you just edited, use your new function to perform the desired action.


### Adding a New Control Application  

To add a new application to the `_controls/hvac/sequences/python/strategies` directory, follow these steps:

1. Open the `_controls/hvac/sequences/python/strategies` directory.

2. Add a new strategy

   Create a new module file in the directory and write the code for your new strategy in the module file. Name the file something descriptive that indicates what the strategy does.

3. Save the module file in the `_controls/hvac/sequences/python/strategies` directory.

4. Open the `__init__.py` file in the `_controls/hvac/sequences/python/strategies` directory.

5. Add module name to the `__all__` list

   Add the name of your new module to the `__all__` list in the `__init__.py` file. This allows other files to import your new module and use the strategy you just created.

6. Save the `__init__.py` file.

7. For running the new application in BOPTEST, create a BOPTEST_interface

   In the `examples/boptest/` directory, create a new `BOPTEST_interface` file that imports your new strategy module and all the functions it uses. The `BOPTEST_interface` should also import the required utility functions.

8. Create a new query

   Create a new query for BOPTest with all the required metadata for your new strategy. 

9. Add a new config file

   For each test case that will use your new strategy, create a new `_config` file in their directories. This file should contain the paths to the corresponding graphs, the path to the new query you created in step 8, and any metadata not available in the graph. Import this file in the `BOPTEST_interface` module.

10. Define a control agent

    In the `BOPTEST_interface`, define a control agent that queries and preprocesses the data using utility functions. The control agent should then send the data to the control strategy by calling the `compute_control()` function.

11. Add a new test_case_interface

    For each test case that will use your new strategy, create a new `test_case_interface` file. This file should import the required utility functions and the corresponding `BOPTEST_interface`. It should also create an application that instantiates the interfaces based on the `_config` file.

12. Save all changes and simulate your new strategy with the _simulation.ipynb_ file in each test case.