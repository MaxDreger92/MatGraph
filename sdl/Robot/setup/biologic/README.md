# Driver for BioLogic Multi-Channel Potentiostats 

* Can be used with all potentiostat models supported by EC-Lab SDK (tested with VMP-3e)
* Designed to be easily extended to support additional techniques.

## Usage and Examples

### Minimal Example

```python
import time
from biologic import connect, BANDWIDTH
from biologic.techniques.ocv import OCVTechnique, OCVParams
from biologic.techniques.ca import CATechnique, CAParams, CAStep

# sequence of techniques to run
techs = [
    OCVTechnique(OCVParams(
        bandwidth=BANDWIDTH.BW_5,
        rest_time_T=2,
        record_every_dT=0.1,
        record_every_dE=0.2,
    )),
    CATechnique(CAParams(
        record_every_dT=0.5,
        record_every_dI=0.1,
        steps=[
            CAStep(-1, 60.0, False), 
        ],
        bandwidth=BANDWIDTH.BW_5,
    )),
]

with connect('USB0') as bl:  # or IP address
    chan = bl.get_channel(1)
    runner = chan.run_techniques(techs)
    for result in runner:
        if result:
            print(result.data)
        else:
            time.sleep(1)
```

### Overview
This software package provides two top-level Python modules. The `kbio` module is a Python wrapper
around the OEM potentiostat driver provided by the EC-Lab SDK. It is based on the OEM Python code
provided by BioLogic but has been **modified** to support the `biologic` module.

The `biologic` module is a high-level potentiostat driver library built on top of `kbio` that has
been designed to provide an easy to use workflow to run electrochemistry technqiues.

#### Connecting to a Potentiostat
To connect to a potentiostat, use the `connect()` function:
```python
from biologic import connect
bl = connect('USB0')  # returns a BioLogic object
```
The argument to the connect function is interpreted according to the EC-Lab documentation for `BL_CONNECT`.
It must be a string referencing either USB devices or an IP address. A command line utility `blfind` is provided
to find and enumerate available potentiostat devices along with the addresses that may be used to access them.
Run `blfind --help` at the system prompt for more information.

The `connect()` function returns a `BioLogic` object. When your application has finished using the potentiostat,
it is a good idea to close the connection:
```python
bl.close()
```

The `BioLogic` object can also be used as a context manager, to ensure that the connection is closed automatically:
```python
with connect('192.168.1.100') as bl:
    ...  # use bl here
```

#### Accessing Potentiostat Channels
To access a potetiostat channel, use the `BioLogic.get_channel()` method by providing a channel number:
```python
chan = bl.get_channel(1)
```

Available channels and channel numbers can be enumerated using `BioLogic.channels()` and
`BioLogic.channel_numbers`. For example:

```python
print(f"Available channels:" + ", ".join(str(n) for n in bl.channel_numbers))
for chan in bl.channels():
    if chan.is_plugged():
        print(f"Channel {chan.num} is plugged in.")
```

#### Technique Parameters
The first step to running a technique is to construct the technique parameters. Each technique has
its own parameter data type that defines the technique's own particular parameter fields.
```python
from biologic import E_RANGE, I_RANGE, BANDWIDTH
from biologic.techniques.ocv import OCVParams

params = OCVParams(
    E_range=E_RANGE.E_RANGE_10V,
    I_range=I_RANGE.I_RANGE_10mA,
    bandwidth=BANDWIDTH.BW_1,
    rest_time_T=2,
    record_every_dT=0.1,
    record_every_dE=0.2,
)
```
All parameter data objects are subtypes of the `TechniqueParams` class, which defines methods common
to all technique parameters.

#### Running Techniques
To run a sequence technique, construct a list of the desired technique objects using their 
parameters and pass that list to the `Channel.run_techniques()` method.
```python
from biologic.techniques.ocv import OCVTechnique
tech = OCVTechnique(params)
runner = chan.run_techniques([tech])
```
The `Channel.run_techniques()` method returns a `TechniqueRunner` object which is used to control the
execution of the techniques and stream data from the active potentiostat channel. 

To stream data from the techniques, use the runner object as an iterator.
```python
for item in runner:
    if item == runner.DataWait or item == runner.Paused:
        time.sleep(1)
    else:
        print(item)
```
When iterated, the runner will yield either a `IndexData` tuple, or one of the control flow signals:
* `TechniqueRunner.DataWait` indicates that further data is not available right now.
* `TechniqueRunner.Paused` indicates that the channel is paused.

Iteration allows user code to control the flow of execution during streaming. For example, it might not be
desirable to sleep inside the main loop of your application, because you want to switch to doing other tasks instead
until more data becomes available.

Both of these signals evaluate to a false truth value, so if the distinction between them isn't important
then you can simply test the yielded value in an if-statement.

Each `IndexData` tuple contains two elements: an index into the original list that can be used
to lookup which technique the data is associated with, and a data object whose fields 
are specific to that technique. For convenience, the list of techniques is stored in the `techniques`
attribute of the runner. 

For example:
```python
for item in runner:
    if item:
        idx, data = item
        tech = runner.techniques[idx]  # now we know which technique the data came from
        print(data)  # a data object produced by the above technique
```

To abort the technique before it is complete, use the `TechniqueRunner.stop()` method.
```python
runner.stop()
```

#### Technique Data

The data objects produced by running the technique are particular to the technique being run. 
Each technique has its own result data type that defines the data fields particular to that technique.

All result data objects are subclasses of `TechniqueData` which defines methods common to all result data objects.

### Installation
The software can be installed using pip. If using a wheel file, you will need to tell pip the directory
where the wheel file is located.
```commandline
pip install -f path/to/wheel/ biologic
```

The necessary EC-Lab SDK binaries are bundled with `kbio`. However if you are connecting using USB, you may also need to install the EC-Lab USB driver.

Alternatively, you can also copy the `biologic` and `kbio` packages directly into your Python's module search path.

## Dependencies
### Interpreter Version
- Python 3.11

### Supported Potentiostat Models
#### VMP3 Family
* VMP2
* VMP3
* BISTAT
* BISTAT2
* MCS_200
* VSP
* SP50
* SP150
* FCT50S
* FCT150S
* CLB500
* CLB2000
* HCP803
* HCP1005
* MPG2
* MPG205
* MPG210
* MPG220
* MPG240
* VMP3E (tested)
* VSP3E
* SP50E
* SP150E

#### VMP300 Family
* SP100
* SP200
* SP300
* VSP300
* VMP300
* SP240
* BP300


## Contact

#### CanmetMATERIALS
183 Longwood Rd S  
Hamilton, ON L8P 0A5   
+1 (905) 645-0683   

Gabriel Birsan <gabriel.birsan@nrcan-rncan.gc.ca>   
Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>   
Dennis Hopewell <dennis.hopewell@nrcan-rncan.gc.ca>    
Frank Benkel <frank.benkel@nrcan-rncan.gcca>  
