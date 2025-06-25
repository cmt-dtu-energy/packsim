# packsim - A simulator of the process of packing particles

`packsim` is a command-line tool and Python library that allows you to simulate the process
of packing particles inside a box container.

Currently, the only process supported involves simulating **up to two types** of 
**hexagonal prismatic particles**, termed `A` and `B`, with the mass content of `B` possibly zero. 
The simulation involving placing the particles in a 3D grid above the bottom of the
container, randomly choosing with particle to place at a given grid point (respecting
the target mass fraction of each particle) and the orientation of the prism's axis.
Gravity is the only force driving the simulation.

With `packsim`, you specify the input parameters for the simulation, and 
the application runs the simulation, saves intermediate files and 
outputs a description of the final packing - essentially, the final
position and orientation of all the particles described in the input.

## Installation

### Pre-requisites

Please notice that, although projects listed below are open-sourced, 
**the STLExtractor dependency requires a MATLAB license**.

- [`packgen`][packgen], responsible for simulating the packing and exporting an intermediate STL file
- [`STLExtractor`][stlextractor], responsible for extracting geometric information from the STL file

[packgen]: https://github.com/cmt-dtu-energy/packgen
[stlextractor]: https://github.com/cmt-dtu-energy/stlextractor

### Installing `packsim`

Install `packsim` with:

```shell
uv pip instal git+https://https://github.com/cmt-dtu-energy/packsim
```

## Usage as command-line tool

```shell
packsim [INPUT_FILE] [-o OUTPUT_FILE] 
```

Notice that

- If `INPUT_FILE` is missing, `packsim` will read from the stdin
- If the output file specification is missing, `packsim` will write to stdout

### Specification of the input file


Each of the type of hexagonal particles should be specified
as a JSON object as in the example:

```json
{
  "radius": 0.2,
  "thickness": 0.1,
  "density": 1
}
```

The input file must contain valid JSON with the valid fields:

```json
{
  "particle_A": {}, // object as described above
  "particle_B": {}, // same as above, but optional if value below is 0
  "mass_fraction_B": 0.2, // a number between 0 and 1 (both inclusive)
  "num_particles_xy": 2, // size of the grid in each of the x and y axis
  "num_particles_z": 4, // size of the grid in the z axis
  "L": 1.0, // size of the box container length in the x and y directions
  "n_sims": 1, // how many random drawings (simulations) to perform
  "cutoff": 0.2 // a number between 0 (exclusive) and 0.5 (exclusive) that indicates how much a margin to cut from the ends of the container
  "cutoff_direction": "x", // direction from which to begin the cutoff process
  "work_dir": "..." // directory where to save the intermediate files
}
```


If `n_sims` is larger than 1, then the simulations are run in parallel.

Each simulation is saved in numbered subdirectories of `work_dir`

### Specification of the output file

The output file is a JSON file with an array of objects, one for each of the
`n_sims` described above.

Each array element is an object with the following fields:

```json
{
  "parameters": {}, // a copy of the resolved [`packgen`](https://github.com/cmt-dtu-energy/packgen/blob/main/examples/parameters.json) input file
  "stl_path" : "", // absolute path to the intermediate stl file
  "blender_path" : "", // absolute path to the intermediate Blender file (useful for producing renderings)
  "extracted_packing": {
    "items": [], // array of objects described below
    "volume": ..., // volume of the boxed container
    "filling_fraction": ..., // how much of the volume above the particles occupy
    "xmin": ..., // minimum x-value of all vertices of all particles,
    // likewise, there are "xmax", "ymin","ymax","zmin","zmax" fields
    "average_alignment_x": ..., // mean value of the orientation of the particles with respect for the "x" axis
    "standard_deviation_alignment_x": ..., // standard deviation of the statistic described above
    // likewise, the fields above are defined for the "y" and "z" direction
    "volume_weighted_average_alignment_x": ..., // same as above, but using each particle's volume as weigth and normalizing with the box volume
    "volume_weighted_standard_deviation_alignment_x": ..., // standard deviation of the statistic described above
    // likewise, the fields above are defined for the "y" and "z" direction
}
```

Each element of the `extracted_packing.items` field is an object describing the final state of each particle:

```json
{
  "radius": 0.2,
  "thickness": 0.1,
  "position": [], // 3D array describing the position
  "normal": [], // 3D array describing the normal orientation,
  "face_rotation": [], // 3D array describing the rotation of the hexagonal face, orthogonal to the "normal" vector
  "volume": ..., // volume of the particle
  "mass": ..., // mass of the particle
  "vertices": [] // 12 x 3 coordinates of the vertices
}
```

