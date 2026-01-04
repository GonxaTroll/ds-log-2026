# Week 01 - Simple path finding

## Anecdote
The other day I stumbled across [this video](https://www.instagram.com/reel/DSJ4wGfCiKb/?igsh=NmxmdGl3NTZzMXEz) (there are plenty like these on social media) and I tried to solve it myself. It depicts a problem where one must step onto each of the squares without using the same path between a pair of squares twice. After a few minutes, I realised there was no way I could do this without repeating any of such paths.  
That reminded me, though, of my past graph theory classes. The elements in the image could be transformed into nodes (squares) and possible edges, and it was all about finding a [Hamiltonian path](https://en.wikipedia.org/wiki/Hamiltonian_path) in the resulting graph. So, reluctant to use my brain cells over such (rather dull) challenges from social media, I decided to implement an automated way to solve them.

## Overview
A couple of notebooks showcasing the usage of Gemini to extract the graph's structure from an image and the construction of it with the *networkx* library.

## Topics Covered
- Graph theory concepts: Hamiltonian / Eulerian graphs
- Simple calls to Gemini API.

## Notes
- As an upgrade, a small agent could be built to properly create the graph (correct possible mistakes in it in a conversational way) and further retrieve the solution to the problem.
