## Label-equivalence-based 3D grain segmentation algorithm benchmark with DREAM3D

For benchmarking, DREAM3D-6.5.168 should be installed in the following directory:

```text
C:\D3D\DREAM3D-6.5.168-Win64
```

After installing DREAM3D, create a folder named `bench` in the DREAM3D installation directory:

```text
C:\D3D\DREAM3D-6.5.168-Win64\bench
```

Then, copy all benchmark source files into the `bench` folder.

The `bench` folder should include the following subfolders, Python scripts, and Windows PowerShell script files:

```text
bench
├── D3D_json
├── D3D_pipeline_log
├── input_txt
├── *.py
└── *.ps1
```

The Python scripts and PowerShell scripts should be executed from the `bench` directory.


## Running the Benchmark

The `run_D3D_bench.ps1` file is used to run `PipelineRunner.exe` in the Windows 11 PowerShell environment.  
This script measures the DREAM3D pipeline execution time and records the results as log files.

### 1. Generate Benchmark ANG Files

For benchmarking the label-equivalence-based 3D grain segmentation algorithm, first open the `ANG_gen.py` file.

In `ANG_gen.py`, modify the following parameters:

```python
mx = 2
my = 2
mz = 2
```

This setting generates the following ANG file:

```text
output_2x2x2.ang
```

The values of `mx`, `my`, and `mz` can be changed from:

```python
mx = 1
my = 1
mz = 1
```

to:

```python
mx = 8
my = 8
mz = 8
```

These parameters control the size of the benchmark ANG file.

### 2. Run the DREAM3D Benchmark

After generating the ANG files, run the PowerShell script in the Windows 11 PowerShell environment:

```powershell
.\run_D3D_bench.ps1
```

This command runs the DREAM3D pipelines and creates log files in the following folder:

```text
D3D_pipeline_log
```


### 3. Run the Label-Equivalence-Based 3D Grain Segmentation Algorithm

To run the label-equivalence-based 3D grain segmentation algorithm, execute the following Python script:

```text
grain_extraction_label_eqv_bench.py
```

In `grain_extraction_label_eqv_bench.py`, you can select the converted ANG file and set the misorientation threshold.

For example:

```python
input_file = "ANG_files/output_1x1x1.ang"
misori_threshold = 3
compare_with_dream3d = True
warming_up = True
```

The option:

```python
compare_with_dream3d = True
```

enables comparison between the label-equivalence-based segmentation result and the DREAM3D segmentation result.

The option:

```python
warming_up = True
```

is used to exclude the compilation time of functions wrapped with Numba from the benchmark timing.






