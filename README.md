# lego-art-map-blog-post

A Manim script that creates an animation which illustrates how I replicated the
[LEGO Art World Map's](https://www.lego.com/en-gb/product/world-map-31203)
projection, starting from WGS-84.

## Output

https://user-images.githubusercontent.com/3501061/154586086-266f8583-57a4-409b-b3bd-23012d664606.mp4

## Requirements

* Docker
* Curl (Or download 110m land and lake shape data from [NaturalEarthData.com])

## Quick-Start

The following commands should render the animation.
It might take a few minutes to complete.

```console
% make download_ne_data
% make setup
% make render
```

[NaturalEarthData.com]: http://naturalearthdata.com
