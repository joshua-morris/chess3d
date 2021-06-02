# 3D Chess
A 3D chess game in OpenGL created for the purposes of assessment for a computer graphics course.
Wavefront OBJ files aren't available in the repository and must be exported from the Blender source.

![](images/board.png)

## Requirements

Create a pipenv sandbox and install dependencies using
```
pipenv install
```

It is also required to export OBJ files from Blender using the given .blend files (objects were ommitted due to large file sizes).

## Usage
Once the virtual environement and objects are available run the game with
```
pipenv run Chess.py
```
in the outmost directory.

## Game Control
|Key|Action|
|:---:|:---:|
|`W`|Move cursor forward|
|`A`|Move cursor left|
|`S`|Move cursor backward|
|`D`|Move cursor right|
|`Space`|Select piece<br>Move piece<br>Cancel move|
