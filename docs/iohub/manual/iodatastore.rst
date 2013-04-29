Using the ioDataStore
======================

**THIS PAGE IS NOT COMPLETE AND WILL BE UPDATED WITHIN 72 HOURS**

Runtime Configuration
-----------------------

	* Specifying if DataStore should be used at all.
	* SPecifying which device types should have events saved to the DataStore
	
ioDataStore File Structure
---------------------------

	* Provide an illustration of the structure.
	* Events are grouped By Device Type
	* Events are saved in table like structures.
	* Event table column names == Event attribute names when accessed online.
	* Pytables and the HDF5 file format are what make the iodataSTore what it is.
	
PyTables Package Data Access
-----------------------------

	* Point to HDF5 Viewer applications
	* Point to Pytables package API.
	* Give overview of how to best access data under some common situations
	* Given a small example of using the pytables PI directly with an ioDataStore HDF5 file.
	
ioDataStore Access Classes
---------------------------

	* Overview of the ExperimentDataAccessUtility class.
	* Give example of how it can be used to easily retieve 'qualified' events from > 1 device.
    * Give example of how to easily visualize the data retrieved using matplotlib.
	
Putting it together
--------------------

	* Go though the process of determining what experiment information should be saved to the ioDataStore along with all the device event data collected.
	* Demonstrate how to do delective event retrieval and calculate a reaction time and response accuracy level.
	* SHow how to plot results based on experiment condition values in matplotlib.
