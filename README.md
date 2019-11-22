### Tow Wise Model Generation in Marc Mentat

This is a brief walk through of the code presented for my undergraduate honours thesis at UNSW. It walks throught the files in here and how to run the code.
Its designed to run with Marc Mentat, and requires the python module, and has been catered to read data from Automated Dynamics "Fibre Placement Manager" software.



## Getting Started

To run the two scripts requires the use of several packages, detailed below:

- Numpy - for general numerical processing
- Scipy, Matplotlib - for plotting any surfaces and curves
- Pandas - for data entry and reading in the FPM data
- Trimesh - This is critial for any of the z-offset calculations
	- Its recommend to install all of trimesh's optional dependencies as the ray queries depend on these
- RTree
- PyEmbree - for faster ray queries (if PyEmbree install poses issues, just installing Embree seems to work fine as well)
- geomdl - for NURBS interpolation. You can use scipy as well but we found this to work better

The easiest way would be to run an anaconda distribution as a lot of these packages are already there apart from trimesh. The other packages you can either install through 

`$ pip install *package*`

or

`$ conda install -c condaforge *package*`

##File Structure
The file structure is set up with most of the relevant script files in the root directory. The only relevant folders are FPM, stl_files and dat_files

FPM contains all the tow data. Each different 'design' has its own folder in the FPM directory with the name of the design (which is referenced later). Each design is separated into ply directories and each ply directory as an individual file for each tow. This structure is important as it is how the import file expects to read it in as.

The file `FPMImport.py` is used to read in this data. The files were designed this way such that it would work with output types other than FPM, but this was the only one we had access to.

The stl_files folder contains any stl files of the original 3D models that can be used by the script.

The dat_files folder contains the serialised data structures output by the python interface to be read into the Marc interface

##Python Interface

The Python interface is the side that reads in the FPM data and pre-processes it to return a data structure that can be read into Marc. The relevant files are as follows

- Tow.py, Ply.py, Point.py are class files for the geometry data
	 - Tow.py also has a lot of helper functions for manipulating tow point
- Import.py - the main file that calls every other function
- Mesh.py - this contains most of the trimesh related helper functions for calculating the z-offset

###Usage

You specify the file as a command line argument, and if you wish to include an stl_file of the original model you add that as an additional argument as well.

`python Import.py <filename> <stlfilename>`

e.g.

`python Import.py flat_panel flat_panel.stl`

##Marc Interface

This is all run through Marc itself. From the program you neded to select the python file to run. 
Main.py is the only file required

At the top of the file, you need to change the file name to the name corresponding to the file used in the python interface.
