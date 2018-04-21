# MPIImageProcessing
Image processing using MPI standard

## Overview
The main aim of project is creating system to distributed image processing. Input data is picture, output data is picture/histogram/error message.

## Description
System is based on client-server architecture &mdash; client is implemented as mobile application (it requests image processing), server (REST server) and calculation node (processes selected part od image) are console applications.

<p align="center"><img src="https://github.com/kazimierczak-robert/MPIImageProcessing/blob/master/Resources/SystemAng.png"></p>
<p align="center"><em>Figure 1. Principle of image processing</em></p>

### Selected image processing algorithms
- histogram
- RGB channel selection
- inversion
- grayscale
- brightness
- contrast 
- gamma
- rotation
- mirror reflection

## Implementation assumptions
- mobile app: Android 5.0+, Kotlin, Android Studio 3.0
- server app: console app, python 3.6, Visual Studio 2017, REST architecture
- calculation node app: console app, python 3.6, Visual Studio 2017, MPI standard

## Attributions


## Credits
* Monika Grądzka
* Robert Kazimierczak
* Kamil Szulc
