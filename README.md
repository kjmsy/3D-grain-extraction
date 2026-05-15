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
