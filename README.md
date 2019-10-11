# SandTable

SandTable provides a web-based user interface to control artistic mechanisms built on CNC platforms, particularly machines that use an x/y motion stage to move a magnet and move a steel ball through sand.

## Getting Started

###Software:



###Hardware:

While you can use SandTable to generate interesting pictures on a screen, the real benefit comes from connecting to a CNC machine. 



### Examples:
* [Michael Dubno's first table](https://makezine.com/2009/08/10/new-york-city-sand-table-project/)
* [Michael Dubno's first table](http://www.atelier-automatik.com/sandtable.html)
* [Mark Rehorst's table](https://drmrehorst.blogspot.com/2018/10/a-3d-printed-sand-table-spice-must-flow.html)

## Built With:
* [numpy](https://numpy.org/) - Python N-dimensional array package
* [pypotrace](https://pypi.org/project/pypotrace/) - Python bindings to potrace
* [potrace](http://potrace.sourceforge.net/) - Bitmap image to vector conversion
* [scipy](https://www.scipy.org/) - Python science/math package
* [Image]
* [bottle](http://bottlepy.org/docs/dev/) - Lightweight Python web framework
* [shapely](https://pypi.org/project/Shapely/) - Python interface to GEOS to operate on planar geometry
* [apscheduler](https://apscheduler.readthedocs.io/en/latest/) - Advanced Python scheduler
* [sqlalchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and object relational manager
* [fontTools](https://github.com/fonttools/fonttools) - Python library for manipulating fonts
* [gphoto2](https://github.com/jim-easterbrook/python-gphoto2) - Python control of cameras

## Deployment:

The system is happy running on Linux (prefered), Macs, and PCs.  Raspberry Pi running Raspbian is the prefered (and most tested) platform. Other platforms require hand-tweaking the installation.

### Raspberry Pi Installation (tested on 2,3,3b+,and 4):
Set the hostname of your machine
Create user "sandtable"
Add "sandtable" to group "sudoers"
Login as "sandtable"
Clone the repository (should be in /home/sandtable/sandtable).
cd sandtable/config
./install.sh

Configure your controller
Configure your machine
Give access to the USB port

Modify local.rc

Reboot

Logs are written to:
* Server logs - /var/logs/server.log
* CNC Machine logs - /var/logs/machd.log
* LED Lighting logs - /var/logs/ledaemon.log
* Scheduler logs - /var/logs/scheduler.log

## Authors:

* **Michael Dubno**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* A big thanks to the entire open-source community who provided a wonderful OS (Linux), a great language (Python), and hundreds of useful libraries which made this project substantially easier to develop.
* This project came about because of a trip to Dean Kamen's house over Christmas. His house is filled with wonderful machines that combine art and science that have been custom built for him. Around New Years I caught Fifth's disease which took over a month to be diagnosed, so I designed my own art and science machine, the sandtable, which I immediately constructed after recovery.
